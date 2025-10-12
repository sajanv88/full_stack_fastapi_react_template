from fastapi import APIRouter, Depends, status

from api.common.dtos.worker_dto import WorkerPayloadDto
from api.common.exceptions import ApiBaseException, InvalidOperationException
from api.common.utils import get_host_main_domain_name, get_logger
from api.core.container import    get_tenant_service
from api.core.exceptions import InvalidSubdomainException, TenantNotFoundException
from api.domain.dtos.tenant_dto import CreateTenantResponseDto, SubdomainAvailabilityDto, TenantDto, TenantListDto, CreateTenantDto, UpdateTenantDto, UpdateTenantResponseDto
from api.domain.dtos.user_dto import CreateUserDto
from api.domain.entities.tenant import Subdomain, Tenant
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.tenant_service import TenantService
from api.infrastructure.messaging.celery_worker import handle_post_tenant_creation, handle_post_tenant_deletion, handle_tenant_dns_update

logger = get_logger(__name__)

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.get("/", response_model=TenantListDto, status_code=status.HTTP_200_OK)
async def list_tenants(
    skip: int = 0, limit: int = 10,
    service: TenantService = Depends(get_tenant_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.HOST_MANAGE_TENANTS]))    
):
    return await service.list_tenants(skip=skip, limit=limit)

@router.post("/", response_model=CreateTenantResponseDto, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: CreateTenantDto,
    service: TenantService = Depends(get_tenant_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.HOST_MANAGE_TENANTS]))
):
    tenant_id = await service.create_tenant(data)
    
    response = CreateTenantResponseDto(id=str(tenant_id))
    
    admin_user = CreateUserDto(
        email=data.admin_email,
        password=data.admin_password,
        first_name=data.first_name,
        last_name=data.last_name,
        gender=data.gender,
        tenant_id=response.id,
        sub_domain=data.subdomain
    )
    payload=WorkerPayloadDto(
        label="post-tenant-creation",
        data=admin_user,
        tenant_id=response.id
    )
    handle_post_tenant_creation.delay(
        payload=payload.model_dump_json()
    )
    return response


@router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_tenant(
    id: str,
    service: TenantService = Depends(get_tenant_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.HOST_MANAGE_TENANTS]))
):
    try:
        tenant: Tenant = await service.get_tenant_by_id(tenant_id=id)
        tenant_doc = await tenant.to_serializable_dict()
        payload=WorkerPayloadDto(
            label="post-tenant-deletion",
            data=TenantDto(**tenant_doc),
            tenant_id=id
        )
        await service.delete_tenant(tenant_id=id)
        handle_post_tenant_deletion.delay(payload=payload.model_dump_json())
        return status.HTTP_202_ACCEPTED
    except TenantNotFoundException as e:
        raise e
    except Exception as e:
        raise ApiBaseException(f"Failed to delete tenant: {str(e)}")


@router.get("/search_by_name/{name}", response_model=TenantDto, status_code=status.HTTP_200_OK)
async def search_by_name(
    name: str,
    service: TenantService = Depends(get_tenant_service)
):

    tenant = await service.find_by_name(name)
    tenant_doc = await tenant.to_serializable_dict()
    return TenantDto(**tenant_doc)


@router.get("/search_by_subdomain/{subdomain}", response_model=TenantDto, status_code=status.HTTP_200_OK)
async def search_by_subdomain(
    subdomain: Subdomain,
    service: TenantService = Depends(get_tenant_service)
):
    tenant = await service.find_by_subdomain(subdomain)
    tenant_doc = await tenant.to_serializable_dict()
    return TenantDto(**tenant_doc)


@router.get("/check_subdomain/{subdomain}", response_model=SubdomainAvailabilityDto, status_code=status.HTTP_200_OK)
async def check_subdomain_availability(
    subdomain: Subdomain,
    service: TenantService = Depends(get_tenant_service)
):
    try: 
        await service.find_by_subdomain(subdomain)
        is_available = False
    except TenantNotFoundException as e:
        is_available = True
    except InvalidSubdomainException as e:
        is_available = False

    return SubdomainAvailabilityDto(is_available=is_available)


@router.post("/update_dns/{tenant_id}", 
            response_model=UpdateTenantResponseDto,
            description=
            f"""
                When bringing your own domain you must map the DNS records for your custom domain to point to our main domain.
                You can do this by adding a CNAME record in your domain's DNS settings.
                Here is an example of how to set it up:
                Type: CNAME
                Name: app
                Value: {get_host_main_domain_name()}
            """,
            status_code=status.HTTP_202_ACCEPTED
        )
async def update_tenant_dns_record(
    tenant_id: str,
    data: UpdateTenantDto,
    current_user: CurrentUser,
    tenant_service: TenantService = Depends(get_tenant_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.HOST_MANAGE_TENANTS, Permission.MANAGE_TENANT_SETTINGS]))
):
    tenant = await tenant_service.get_tenant_by_id(tenant_id)
    if tenant.custom_domain_status == "activation-progress":
        return UpdateTenantResponseDto(
            message="Your previous custom domain update is still in progress. Please wait until it is processed."
        )
    
    if tenant.custom_domain_status == "active":
        return UpdateTenantResponseDto(
            message="Your custom domain is already active. If you want to change it, please contact support."
        )
    
    payload=WorkerPayloadDto[dict[str, str]](
        label="update-tenant-dns",
        data={
            "custom_domain": data.custom_domain,
            "user_id": str(current_user.id),
        },
        tenant_id=str(tenant.id)
    )
    tenant.custom_domain = data.custom_domain
    tenant.is_active = data.is_active if data.is_active is not None else tenant.is_active
    tenant.custom_domain_status = "activation-progress" if data.custom_domain else None
    await tenant.save()
    handle_tenant_dns_update.delay(
        payload=payload.model_dump_json()
    )
    return UpdateTenantResponseDto(
        message="We have received your request. The changes will reflect in a few minutes. And email notification will be sent."
    )

@router.get("/check_dns/{tenant_id}", response_model=UpdateTenantResponseDto, status_code=status.HTTP_200_OK)
async def check_dns_status(
    tenant_id: str,
    current_user: CurrentUser,
    tenant_service: TenantService = Depends(get_tenant_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.HOST_MANAGE_TENANTS, Permission.MANAGE_TENANT_SETTINGS]))
):
    tenant_doc = await tenant_service.get_tenant_by_id(tenant_id)
    payload=WorkerPayloadDto[dict[str, str]](
        label="update-tenant-dns",
            data={
                "custom_domain": tenant_doc.custom_domain,
                "user_id": str(current_user.id),
            },
            tenant_id=str(tenant_doc.id)
        )
    if not tenant_doc.custom_domain:
        raise InvalidOperationException("No custom domain is set for this tenant.")
    
    if tenant_doc.custom_domain_status == "activation-progress":
        handle_tenant_dns_update.delay(
            payload=payload.model_dump_json()
        )
        return UpdateTenantResponseDto(
            message="Your custom domain activation is still in progress. Please wait until it is processed."
        )
    
    if tenant_doc.custom_domain_status == "active":
        return UpdateTenantResponseDto(
            message="Your custom domain is already active. No further action is needed."
        )
    
    if tenant_doc.custom_domain_status == "failed":
        
        handle_tenant_dns_update.delay(
            payload=payload.model_dump_json()
        )
        return UpdateTenantResponseDto(
            message="Your custom domain activation previously failed. Please update your DNS settings and try again."
        )

    return UpdateTenantResponseDto(
        message="DNS status check completed successfully."
    )
