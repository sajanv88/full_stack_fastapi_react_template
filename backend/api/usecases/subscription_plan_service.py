from api.common.exceptions import InvalidOperationException
from api.domain.dtos.subcription_plan_dto import CreateSubscriptionPlanDto, SubscriptionPlanDto
from api.infrastructure.persistence.repositories.subscription_plan_repository_impl import SubscriptionPlanRepository


class SubscriptionPlanService:
    def __init__(self, subscription_plan_repository: SubscriptionPlanRepository):
        self.subscription_plan_repository: SubscriptionPlanRepository = subscription_plan_repository
    
    async def get_subscription_plan_by_id(self, subscription_id: str) -> SubscriptionPlanDto | None:
        result = await self.subscription_plan_repository.get_subscription_plan_by_id(subscription_id)
        if result:
            return SubscriptionPlanDto(**result.model_dump())
        return None
    
    async def get_subscription_plans_by_tenant(self, tenant_id: str) -> SubscriptionPlanDto | None:
        result = await self.subscription_plan_repository.get_subscription_plans_by_tenant(tenant_id)
        if result:
            return SubscriptionPlanDto(**result.model_dump())
        return None
    
    async def get_subscription_plan_by_user_id(self, user_id: str) -> SubscriptionPlanDto | None:
        result = await self.subscription_plan_repository.get_subscription_plan_by_user_id(user_id)
        if result:
            return SubscriptionPlanDto(**result.model_dump())
        return None

    async def create_trial_plan_for_tenant(self, tenant_id: str, plan_id: str):

        subscription_plan = CreateSubscriptionPlanDto(
            tenant_id=tenant_id,
            plan_id=plan_id,
            is_trial=True,
            user_id=None,
            actor="tenant",
            plan_level={"premium": 2}
        )
        result = await self.subscription_plan_repository.create_subscription_plan(subscription_plan=subscription_plan)
        if result is None:
            raise InvalidOperationException("Failed to create trial subscription plan.")
