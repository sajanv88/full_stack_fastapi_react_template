from api.common.utils import get_logger
from api.core.exceptions import ProductException, ProductNotFoundException
from api.domain.dtos.product_dto import CreateProductDto, ProductDto, ProductListDto
from api.domain.entities.stripe_settings import ScopeType
from api.infrastructure.externals.stripe_resolver import StripeResolver
from api.infrastructure.persistence.repositories.payment_repository_impl import PaymentRepository

logger = get_logger(__name__)

class ProductService:
    def __init__(self, payment_repository: PaymentRepository, stripe_resolver: StripeResolver):
        self.payment_repository: PaymentRepository = payment_repository
        self.stripe_resolver: StripeResolver = stripe_resolver

    async def list_products(self, scope: ScopeType, show_active: bool = True) -> ProductListDto:
        sc = await self.stripe_resolver.get_stripe_client(scope=scope)
        result =  await sc.v1.products.list_async(params={"limit": 100, "active": show_active})
        return ProductListDto(products=[product for product in result.data],  has_more=result.has_more)
    
    async def get_product_by_id(self, product_id: str,  scope: ScopeType) -> ProductDto:
        sc = await self.stripe_resolver.get_stripe_client(scope=scope)
        product = await sc.v1.products.retrieve_async(id=product_id)
        if not product:
            raise ProductNotFoundException(f"Product with ID {product_id} not found.")
        return ProductDto(id=product.id, name=product.name, description=product.description, active=product.active, tax_code=product.tax_code) 

    async def create_product(self, product_dto: CreateProductDto, scope: ScopeType):
        try:
            sc = await self.stripe_resolver.get_stripe_client(scope=scope)
            params = product_dto.model_dump()
            await sc.v1.products.create_async(params=params)
            logger.debug(f"Product created successfully in {scope} scope.")
        except Exception as e:
            # Handle specific exceptions if needed
            logger.error(f"Failed to create product: {str(e)}")
            raise ProductException(f"Failed to create product: {str(e)}") from e

    async def update_product(self, product_id: str, product_dto: CreateProductDto, scope: ScopeType):
        try:
            sc = await self.stripe_resolver.get_stripe_client(scope=scope)
            existing_product = await sc.v1.products.retrieve_async(id=product_id)
            if not existing_product:
                raise ProductNotFoundException(f"Product with ID {product_id} not found.")
            
            sc = await self.stripe_resolver.get_stripe_client(scope=scope)
            params = product_dto.model_dump()
            await sc.v1.products.update_async(id=product_id, params=params)
            logger.debug(f"Product with ID {product_id} updated successfully in {scope} scope.")
        except Exception as e:
            # Handle specific exceptions if needed
            logger.error(f"Failed to update product: {str(e)}")
            raise ProductNotFoundException(f"{str(e)}") from e

    async def delete_product(self, product_id: str, scope: ScopeType):
        try:
            sc = await self.stripe_resolver.get_stripe_client(scope=scope)
            await sc.v1.products.delete_async(id=product_id)
            logger.debug(f"Product with ID {product_id} deleted successfully in {scope} scope.")
        except Exception as e:
            # Handle specific exceptions if needed
            logger.error(f"Failed to delete product: {str(e)}")
            raise ProductNotFoundException(f"Product with ID {product_id} not found.") from e
