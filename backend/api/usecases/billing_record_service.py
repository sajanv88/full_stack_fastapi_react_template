from api.common.utils import get_logger
from api.core.exceptions import BillingRecordException, BillingRecordNotFoundException
from api.domain.dtos.billing_dto import CreatePlanDto, InvoiceListDto, PlanDto, PlanListDto, UpdatePlanDto
from api.domain.entities.stripe_settings import ScopeType
from api.infrastructure.externals.stripe_resolver import StripeResolver
from api.infrastructure.persistence.repositories.payment_repository_impl import  BillingRecordRepository, PaymentRepository

logger = get_logger(__name__)

class BillingRecordService:
    def __init__(
            self, 
            payment_repository: PaymentRepository,
            billing_record_repository: BillingRecordRepository,
            stripe_resolver: StripeResolver
        ):

        self.payment_repository: PaymentRepository = payment_repository
        self.billing_record_repository: BillingRecordRepository = billing_record_repository
        self.stripe_resolver: StripeResolver = stripe_resolver

    async def list_plans(self, scope: ScopeType) -> PlanListDto:
        sc = await self.stripe_resolver.get_stripe_client(scope=scope)
        result = await sc.v1.plans.list_async(params={"limit": 100})
        return PlanListDto(plans=[plan for plan in result.data],  has_more=result.has_more)

    async def create_plan(self, new_plan: CreatePlanDto, scope: ScopeType) -> None:
        try:
            sc = await self.stripe_resolver.get_stripe_client(scope=scope)
            await sc.v1.plans.create_async(params={
                "amount": new_plan.amount,
                "interval": new_plan.interval,
                "currency": new_plan.currency,
                "product": new_plan.product_id
            })
        except Exception as e:
            logger.error(f"Error creating plan : {e}")
            raise BillingRecordException(str(e))

    async def update_plan(self, plan_id: str, update_plan: UpdatePlanDto, scope: ScopeType) -> None:
        try:
            sc = await self.stripe_resolver.get_stripe_client(scope=scope)
            await sc.v1.plans.update_async(plan=plan_id, params={
                "active": update_plan.active,
                "trial_period_days": update_plan.trial_period_days,
                "metadata": update_plan.metadata or {}
            })
        except Exception as e:
            logger.error(f"Error updating plan {plan_id}: {e}")
            raise BillingRecordNotFoundException(plan_id)

    async def get_plan(self, plan_id: str, scope: ScopeType) -> PlanDto:
        try:
            sc = await self.stripe_resolver.get_stripe_client(scope=scope)
            return await sc.v1.plans.retrieve_async(plan=plan_id)
        except Exception as e:
            logger.error(f"Error retrieving plan {plan_id}: {e}")
            raise BillingRecordNotFoundException(plan_id)

    async def delete_plan(self, plan_id: str, scope: ScopeType) -> None:
        sc = await self.stripe_resolver.get_stripe_client(scope=scope)
        result = await sc.v1.plans.delete_async(plan=plan_id)
        if result.deleted is False:
            raise BillingRecordException(f"Unable to delete the plan {plan_id}.")
        
    async def list_invoices(self, scope: ScopeType) -> InvoiceListDto:
        sc = await self.stripe_resolver.get_stripe_client(scope=scope)
        result = await sc.v1.invoices.list_async(params={"limit": 100})
        return InvoiceListDto(invoices=[invoice for invoice in result.data], has_more=result.has_more)