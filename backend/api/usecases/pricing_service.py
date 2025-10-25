from api.domain.dtos.pricing_dto import CreatePricingDto, PricingListDto
from api.domain.entities.stripe_settings import ScopeType
from api.infrastructure.externals.stripe_resolver import StripeResolver
from api.infrastructure.persistence.repositories.payment_repository_impl import PaymentRepository


class PricingService:
    def __init__(self, payment_repository: PaymentRepository, stripe_resolver: StripeResolver):
        self.payment_repository: PaymentRepository = payment_repository
        self.stripe_resolver: StripeResolver = stripe_resolver
    
    async def create_price(self, price: CreatePricingDto, scope: ScopeType):
        sc = await self.stripe_resolver.get_stripe_client(scope=scope)
        return await sc.v1.prices.create_async(params=price.model_dump())
    
    async def list_prices(self, scope: ScopeType):
        sc = await self.stripe_resolver.get_stripe_client(scope=scope)
        result = await sc.v1.prices.list_async(params={"limit": 100})
        return PricingListDto(products=[product for product in result.data],  has_more=result.has_more)
    
    
