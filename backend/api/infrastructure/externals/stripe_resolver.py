import stripe
from api.core.config import settings

from api.core.exceptions import StripeSettingsNotFoundException
from api.domain.entities.stripe_settings import ScopeType
from api.infrastructure.persistence.repositories.payment_repository_impl import StripeSettingsRepository


class StripeResolver(StripeSettingsRepository):
    def __init__(self):
        super().__init__()
        self.client = stripe.StripeClient(api_key=settings.stripe_api_key)

    async def get_stripe_client(self, scope: ScopeType) -> stripe.StripeClient:
        if scope == "tenant":

            tenant_stripe_api_key = await super().single_or_none()
            if tenant_stripe_api_key is None:
                raise StripeSettingsNotFoundException(f"No Stripe settings found")
            
            return stripe.StripeClient(api_key=tenant_stripe_api_key)
        
        return self.client
