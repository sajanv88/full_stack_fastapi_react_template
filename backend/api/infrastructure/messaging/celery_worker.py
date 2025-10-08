import asyncio
import os
import time
from celery import Celery

from api.common.dtos.worker_dto import WorkerPayloadDto
from api.common.utils import get_logger
from api.core.container import get_cloudflare_dns_service, get_role_service, get_tenant_service, get_user_service
from api.domain.dtos.tenant_dto import CreateTenantDto, TenantListDto
from api.domain.dtos.user_dto import CreateUserDto
from api.infrastructure.background.add_dns_record_task_service import AddDnsRecordTaskService
from api.infrastructure.persistence.mongodb import Database, models
from api.infrastructure.background.post_tenant_creation_task_service import PostTenantCreationTaskService

broker_url = os.getenv("CELERY_BROKER_URL")
backend_url = os.getenv("CELERY_RESULT_BACKEND")
mongo_uri = os.getenv("MONGO_URI")
mongo_db_default = os.getenv("MONGO_DB_NAME")

logger = get_logger(__name__)

celery_app = Celery(
    'worker',
    broker=broker_url,
    backend=backend_url,
    include=['api.infrastructure.messaging.celery_worker']
)



## Tenant related tasks
@celery_app.task(default_retry_delay=60, max_retries=5)
def handle_post_tenant_creation(payload: str):
    asyncio.run(_handle_post_tenant_creation_async(payload))


@celery_app.task(default_retry_delay=60, max_retries=5)
def handle_post_tenant_deletion(payload: str):
    asyncio.run(_handle_post_tenant_deletion_async(payload))

@celery_app.task(default_retry_delay=60, max_retries=5)
def handle_tenant_dns_update(payload: str):
    asyncio.run(_handle_tenant_dns_update_async(payload))



async def _handle_post_tenant_creation_async(payload: str):
    worker_payload = WorkerPayloadDto[CreateUserDto].model_validate_json(payload)
    logger.info(f"Admin user details: {worker_payload.data}")
    logger.info(f"Handling task with label: {worker_payload.label}")
    if worker_payload.label == "post-tenant-creation":
        db_name = f"tenant_{worker_payload.tenant_id}"
        db = Database(uri=mongo_uri, models=models)
        await db.init_db(db_name=db_name, is_tenant=True)
        worker_payload.data.tenant_id = worker_payload.tenant_id # Set tenant_id in admin user data DTO

        logger.info(f"Starting post-tenant-creation tasks for tenant_id: {worker_payload.tenant_id}")
        logger.info(f"Admin user details: {worker_payload.data.email}, Tenant ID: {worker_payload.tenant_id}")
        user_service = get_user_service()
        role_service = get_role_service()
        post_tenant_creation_service = PostTenantCreationTaskService(
            user_service=user_service,
            role_service=role_service
        )
        await post_tenant_creation_service.enqueue(admin_user=worker_payload.data)
        await db.close()

async def _handle_post_tenant_deletion_async(payload: str):
    worker_payload = WorkerPayloadDto[None].model_validate_json(payload)
    logger.info(f"Handling task with label: {worker_payload.label}")
    if worker_payload.label == "post-tenant-deletion":
        logger.info(f"Starting post-tenant-deletion tasks for tenant_id: {worker_payload.tenant_id}")
        db_name = f"tenant_{worker_payload.tenant_id}"
        db = Database(uri=mongo_uri, models=models)
        await db.init_db(db_name=db_name, is_tenant=True)
        await db.drop()
        await db.close()
        logger.warning(f"Completed post-tenant-deletion tasks for tenant_id: {worker_payload.tenant_id} - Database dropped.")


async def _handle_tenant_dns_update_async(payload: str):
    worker_payload = WorkerPayloadDto[CreateTenantDto].model_validate_json(payload)
    logger.info(f"Handling task with label: {worker_payload.label}")
    if worker_payload.label == "update-tenant-dns":
        # Implement DNS update logic here
        subdomain = worker_payload.data.subdomain.split('.')[0], # Extract subdomain part before the main domain
        db = Database(uri=mongo_uri, models=models)
        await db.init_db(db_name=mongo_db_default, is_tenant=False)
        cloudflare_service = get_cloudflare_dns_service()
        dns_service = AddDnsRecordTaskService(cloudflare_service=cloudflare_service)
        await dns_service.enqueue(subdomain=subdomain, email_to=worker_payload.data.admin_email)
        await db.close()
        logger.info(f"Completed DNS update for subdomain: {worker_payload.data}")




