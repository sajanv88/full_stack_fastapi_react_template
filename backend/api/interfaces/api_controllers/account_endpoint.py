from typing import Annotated
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from api.common.dtos.token_dto import TokenSetDto
from api.common.dtos.worker_dto import WorkerPayloadDto
from api.common.utils import get_logger
from api.core.container import get_auth_service
from api.domain.dtos.login_dto import LoginRequestDto
from api.domain.dtos.user_dto import CreateUserDto
from api.infrastructure.messaging.celery_worker import handle_post_tenant_creation
from api.interfaces.middlewares.tenant_middleware import get_tenant_id
from api.usecases.auth_service import AuthService

logger = get_logger(__name__)

router = APIRouter(prefix="/account", tags=["Account"])

@router.post("/login", response_model=TokenSetDto, status_code=status.HTTP_200_OK)
async def login(
    login_request: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
    x_tenant_id: str = Depends(get_tenant_id)
):
    logger.info(f"Login attempt for user: {login_request.username} x_tenant_id: {x_tenant_id}")
    response: TokenSetDto = await auth_service.login(LoginRequestDto(
        email=login_request.username,
        password=login_request.password
    ))
    return response


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: CreateUserDto,
    auth_service: AuthService = Depends(get_auth_service),
    x_tenant_id: PydanticObjectId | None = Depends(get_tenant_id)
):
    logger.info(f"Register attempt for user: {data.email} x_tenant_id: {x_tenant_id}")

    if x_tenant_id is not None:
        data.tenant_id = x_tenant_id
      
    def process_user_creation(tenant_id: PydanticObjectId):
        logger.info(f"Processing user creation for tenant_id: {tenant_id}")
        data.tenant_id = tenant_id
        payload=WorkerPayloadDto[CreateUserDto](
            label="post-tenant-creation",
            data=data,
            tenant_id=str(tenant_id)
        )
        handle_post_tenant_creation.delay(
            payload=payload.model_dump_json()
        )
        
    await auth_service.register(data, process_user_creation)
    return status.HTTP_201_CREATED
        

    