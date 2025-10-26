from fastapi import APIRouter, Depends, status

from api.core.container import get_billing_record_service
from api.domain.dtos.billing_dto import CreatePlanDto, InvoiceListDto, PlanDto, PlanListDto, UpdatePlanDto
from api.infrastructure.security.current_user import CurrentUser, CurrentUserOptional
from api.usecases.billing_record_service import BillingRecordService


router = APIRouter(prefix="/billing")
router.tags = ["Stripe - Billing"]

@router.get("/plans", summary="List available plans", response_model=PlanListDto)
async def list_plans(
    current_user_optional: CurrentUserOptional,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    scope = "host"
    if current_user_optional and current_user_optional.tenant_id:
        scope = "tenant"
    
    return await billing_service.list_plans(scope=scope)

@router.get("/plans/{plan_id:path}", summary="Retrieve a plan details", response_model=PlanDto)
async def get_plan(
    plan_id: str,
    current_user_optional: CurrentUserOptional,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    scope = "host"
    if current_user_optional and current_user_optional.tenant_id:
        scope = "tenant"

    return await billing_service.get_plan(plan_id=plan_id, scope=scope)


@router.delete("/plans/{plan_id:path}", summary="Delete existing plan", status_code=status.HTTP_202_ACCEPTED)
async def delete_plan(
    plan_id: str,
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    scope = "host"
    if current_user.tenant_id:
        scope = "tenant"

    return await billing_service.delete_plan(plan_id=plan_id, scope=scope)


@router.post("/plans/create", summary="Create a new plan", status_code=status.HTTP_201_CREATED)
async def create_plan(
    new_plan: CreatePlanDto,
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    scope = "host"
    if current_user.tenant_id:
        scope = "tenant"

    await billing_service.create_plan(new_plan=new_plan, scope=scope)


@router.patch("/plans/{plan_id:path}/update", summary="Update a existing plan", status_code=status.HTTP_204_NO_CONTENT)
async def update_plan(
    plan_id: str,
    updated_plan: UpdatePlanDto,
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    scope = "host"
    if current_user.tenant_id:
        scope = "tenant"

    await billing_service.update_plan(plan_id=plan_id, updated_plan=updated_plan, scope=scope)



@router.get("/invoices", summary="List invoices", response_model=InvoiceListDto)
async def list_invoices(
    current_user: CurrentUser,
    billing_service: BillingRecordService = Depends(get_billing_record_service)
):
    scope = "host"
    if current_user.tenant_id:
        scope = "tenant"

    return await billing_service.list_invoices(scope=scope)
    
    