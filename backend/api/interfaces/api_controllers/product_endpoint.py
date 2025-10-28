from fastapi import APIRouter, Depends, status
from fastapi.params import Query

from api.core.container import get_product_service
from api.domain.dtos.product_dto import CreateProductDto, ProductListDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.product_service import ProductService


router = APIRouter(
    prefix="/products",
    dependencies=[
        Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_PRODUCTS_AND_PRICING]))
    ]
)
router.tags = ["Stripe - Products"]

@router.get("/", summary="List Products", response_model=ProductListDto)
async def list_products(
    current_user: CurrentUser,
    product_service: ProductService = Depends(get_product_service),
    active: bool = Query(default=True, description="Filter active products, defaults to True")
):
    scope = "tenant" if current_user.tenant_id else "host"
    return await product_service.list_products(scope=scope, show_active=active)

@router.post("/", summary="Create a Product", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_dto: CreateProductDto,
    current_user: CurrentUser,
    product_service: ProductService = Depends(get_product_service)
):
    scope = "tenant" if current_user.tenant_id else "host"
    await product_service.create_product(product_dto=product_dto, scope=scope)
    return status.HTTP_201_CREATED
    
@router.patch("/{product_id:path}", summary="Update a Product", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(
    product_id: str,
    product_dto: CreateProductDto,
    current_user: CurrentUser,
    product_service: ProductService = Depends(get_product_service)
):
    scope = "tenant" if current_user.tenant_id else "host"
    await product_service.update_product(product_id=product_id, product_dto=product_dto, scope=scope)
    return status.HTTP_204_NO_CONTENT

@router.delete("/{product_id:path}", summary="Delete a Product", status_code=status.HTTP_202_ACCEPTED)
async def delete_product(
    product_id: str,
    current_user: CurrentUser,
    product_service: ProductService = Depends(get_product_service)
):
    scope = "tenant" if current_user.tenant_id else "host"
    await product_service.delete_product(product_id=product_id, scope=scope)
    return status.HTTP_202_ACCEPTED
