import asyncio
import os
from celery import Celery

from api.common.dtos.worker_dto import WorkerPayloadDto
from api.common.utils import get_host_main_domain_name, get_logger
from api.core.container import  get_dns_resolver, get_role_service, get_tenant_service, get_user_service
from api.domain.dtos.user_dto import CreateUserDto, UserDto
from api.domain.entities.user import User
from api.infrastructure.externals.dns_resolver import DnsResolver
from api.infrastructure.persistence.mongodb import Database, models
from api.infrastructure.background.post_tenant_creation_task_service import PostTenantCreationTaskService
from api.usecases.tenant_service import TenantService

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



async def _get_current_tenant_db(tenant_id: str) -> Database:
    db_name = f"tenant_{tenant_id}"
    db = Database(uri=mongo_uri, models=models)
    await db.init_db(db_name=db_name, is_tenant=True)
    return db

async def _handle_post_tenant_creation_async(payload: str):
    worker_payload = WorkerPayloadDto[CreateUserDto].model_validate_json(payload)
    logger.info(f"Admin user details: {worker_payload.data}")
    logger.info(f"Handling task with label: {worker_payload.label}")
    if worker_payload.label == "post-tenant-creation":
        db = await _get_current_tenant_db(tenant_id=worker_payload.tenant_id)
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
        db = await _get_current_tenant_db(tenant_id=worker_payload.tenant_id)
        await db.drop()
        await db.close()
        logger.warning(f"Completed post-tenant-deletion tasks for tenant_id: {worker_payload.tenant_id} - Database dropped.")


async def _handle_tenant_dns_update_async(payload: str):
    worker_payload = WorkerPayloadDto[dict[str, str]].model_validate_json(payload)
    logger.info(f"Handling task with label: {worker_payload.label}")
    if worker_payload.label == "update-tenant-dns":
        hostname = worker_payload.data["custom_domain"]
        db = Database(uri=mongo_uri, models=models)
        await db.init_db(db_name=mongo_db_default, is_tenant=False)
        dns_service: DnsResolver = get_dns_resolver()
        try:
            result = await dns_service.resolve(hostname=hostname, expected_target=get_host_main_domain_name())
            if result:
                logger.info(f"DNS for {hostname} is correctly pointing to {get_host_main_domain_name()}. No action needed.")
                await db.close()
                asyncio.run(
                    _notify_dns_status(
                        tenant_id=worker_payload.tenant_id,
                        user_id=worker_payload.data["user_id"],
                        is_success=True,
                        message=f"DNS for {hostname} is correctly pointing to {get_host_main_domain_name()}.",
                        hostname=hostname
                    )
                )
                asyncio.run(_update_tenant_custom_domain_status(tenant_id=worker_payload.tenant_id, status="active"))
                logger.info(f"Completed DNS update for subdomain: {worker_payload.data}")
            else:
                logger.warning(f"DNS for {hostname} is NOT pointing to {get_host_main_domain_name()}.")
                raise Exception("DNS resolution did not return expected target.")
            await db.close()
        except Exception as e:
            logger.error(f"Error occurred while checking DNS for {hostname}: {e}")
            logger.info(f"DNS for {hostname} is NOT pointing to {get_host_main_domain_name()}. Notifying admin user.")
            asyncio.run(
                _notify_dns_status(
                    tenant_id=worker_payload.tenant_id,
                    user_id=worker_payload.data["user_id"],
                    is_success=False,
                    message=f"DNS for {hostname} is NOT pointing to {get_host_main_domain_name()}. Please update your DNS settings.",
                    hostname=hostname
                )
            )
            asyncio.run(_update_tenant_custom_domain_status(tenant_id=worker_payload.tenant_id, status="failed"))
        


async def _notify_dns_status(tenant_id: str, user_id: str, is_success: bool, message: str, hostname: str):
    db = await _get_current_tenant_db(tenant_id=tenant_id)
    user_service = get_user_service()
    admin_user: User = await user_service.get_user_by_id(user_id=user_id)
    admin_user_dto = await admin_user.to_serializable_dict()
    dns_service: DnsResolver = get_dns_resolver()
    dns_service.notify_dns_status(
        user_info=UserDto(**admin_user_dto),
        hostname=hostname,
        is_success=is_success,
        message=message
    )
    await db.close()



async def _update_tenant_custom_domain_status(tenant_id: str, status: str):
    logger.info(f"Updating tenant {tenant_id} custom_domain_status to {status}")
    db = Database(uri=mongo_uri, models=models)
    await db.init_db(db_name=mongo_db_default, is_tenant=False)
    tenant_service: TenantService = get_tenant_service()
    tenant = await tenant_service.get_tenant_by_id(tenant_id=tenant_id)
    tenant.custom_domain_status = status
    await tenant.save()
    await db.close()
    logger.info(f"Updated tenant {tenant_id} custom_domain_status to {status}")