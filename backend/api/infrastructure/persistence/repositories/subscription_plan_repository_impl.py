# This repository is used to represent subscription plans in the system Not used by Stripe directly

from beanie import PydanticObjectId
from api.common.audit_logs_repository import AuditLogRepository
from api.common.base_repository import BaseRepository
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.dtos.subcription_plan_dto import CreateSubscriptionPlanDto
from api.domain.entities.subscription_plan import SubscriptionPlan


class SubscriptionPlanRepository(BaseRepository[SubscriptionPlan], AuditLogRepository):
    def __init__(self):
        super().__init__(SubscriptionPlan)

    async def get_subscription_plan_by_id(self, subscription_id: str) -> SubscriptionPlan | None:
        return await super().get(id=subscription_id)
    
    async def get_subscription_plan_by_user_id(self, user_id: str) -> SubscriptionPlan | None:
        return await super().single_or_none(user_id=PydanticObjectId(user_id))

    async def get_subscription_plans_by_tenant(self, tenant_id: str) -> SubscriptionPlan | None:
        return await super().single_or_none(tenant_id=PydanticObjectId(tenant_id))
    
    async def create_subscription_plan(self, subscription_plan: CreateSubscriptionPlanDto) -> PydanticObjectId | None:
        subcription = SubscriptionPlan(
            tenant_id=PydanticObjectId(subscription_plan.tenant_id) if subscription_plan.tenant_id else None,
            user_id=PydanticObjectId(subscription_plan.user_id) if subscription_plan.user_id else None,
            plan_id=subscription_plan.plan_id,
            is_trial=subscription_plan.is_trial,
            actor=subscription_plan.actor,
            plan_level=subscription_plan.plan_level,
        )
        result = await super().create(subcription.model_dump(exclude_none=True))
        await self.add_audit_log(AuditLogDto(
            action="create",
            entity="SubscriptionPlan",
            user_id=str(subscription_plan.user_id),
            changes={"Info": "Created new subscription plan with id " + str(result.id)},
            tenant_id=str(subscription_plan.tenant_id) if subscription_plan.tenant_id else None
        ))
        return result.id

    async def update_subscription_plan(self, subscription_id: str, update_data: SubscriptionPlan) -> None:
        await super().update(subscription_id, update_data.model_dump(exclude_none=True))
        await self.add_audit_log(AuditLogDto(
            action="update",
            entity="SubscriptionPlan",
            user_id=str(update_data.user_id),
            changes={"Info": "Updated subscription plan with id " + subscription_id},
            tenant_id=str(update_data.tenant_id) if update_data.tenant_id else None
        ))

    async def delete_subscription_plan(self, subscription_id: str) -> None:
        exisiting =  await self.get_subscription_plan_by_id(subscription_id)
        if exisiting is None:
            await self.add_audit_log(AuditLogDto(
                action="delete",
                entity="SubscriptionPlan",
                user_id=None,
                changes={"Info": "Attempted to delete non-existing subscription plan with id " + subscription_id},
                tenant_id=None
            ))
            return
        await super().delete(subscription_id)
        await self.add_audit_log(AuditLogDto(
            action="delete",
            entity="SubscriptionPlan",
            user_id=str(exisiting.user_id) if exisiting.user_id else None,
            changes={"Info": "Deleted subscription plan with id " + subscription_id},
            tenant_id=str(exisiting.tenant_id) if exisiting.tenant_id else None
        ))
