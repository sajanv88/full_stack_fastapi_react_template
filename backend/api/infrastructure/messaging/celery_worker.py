import asyncio

from celery import Celery
from api.common.dtos.worker_dto import WorkerPayloadDto
from api.core.config import settings
from api.common.utils import get_logger
from api.core.container import get_role_service, get_user_service
from api.domain.dtos.user_dto import CreateUserDto
from api.infrastructure.persistence.mongodb import Database, models
from api.infrastructure.background.post_tenant_creation_task_service import PostTenantCreationTaskService


logger = get_logger(__name__)

celery_app = Celery(
    'worker',
    broker=settings.redis_uri,
    backend=settings.redis_uri,
    include=['api.infrastructure.messaging.celery_worker']
)













## Tenant related tasks
@celery_app.task(default_retry_delay=60, max_retries=5)
def handle_post_tenant_creation(payload: str):
    asyncio.run(_handle_post_tenant_creation_async(payload))


@celery_app.task(default_retry_delay=60, max_retries=5)
def handle_post_tenant_deletion(payload: str):
    asyncio.run(_handle_post_tenant_deletion_async(payload))


async def _handle_post_tenant_creation_async(payload: str):
    worker_payload = WorkerPayloadDto[CreateUserDto].model_validate_json(payload)
    logger.info(f"Admin user details: {worker_payload.data}")
    logger.info(f"Handling task with label: {worker_payload.label}")
    if worker_payload.label == "post-tenant-creation":
        db_name = f"tenant_{worker_payload.tenant_id}"
        db = Database(uri=settings.mongo_uri, models=models)
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
        db = Database(uri=settings.mongo_uri, models=models)
        await db.init_db(db_name=db_name, is_tenant=True)
        await db.drop()
        await db.close()
        logger.warning(f"Completed post-tenant-deletion tasks for tenant_id: {worker_payload.tenant_id} - Database dropped.")