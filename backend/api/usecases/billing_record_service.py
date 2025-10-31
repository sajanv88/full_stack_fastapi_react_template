from stripe import StripeClient
from api.common.utils import get_logger
from api.core.exceptions import BillingRecordException, BillingRecordNotFoundException
from api.domain.dtos.billing_dto import BillingRecordListDto, CreatePlanDto, InvoiceListDto, PlanDto, PlanListDto, UpdatePlanDto
from api.domain.dtos.checkout_dto import CheckoutRequestDto
from api.domain.entities.stripe_settings import ActorType, BillingRecord, ScopeType
from api.infrastructure.externals.stripe_resolver import StripeResolver
from api.infrastructure.persistence.repositories.billing_record_repository_impl import BillingRecordRepository
from api.infrastructure.persistence.repositories.payment_repository_impl import PaymentRepository

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
        if len(result.data) == 0:
            return PlanListDto(plans=[], has_more=False)
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
    


    async def create_host_check_out_session_for_tenant(self, frontend_url: str, checkout_req: CheckoutRequestDto) -> str:
        """
        Create a Stripe checkout session for host scope for a tenant
        """
        sc: StripeClient = await self.stripe_resolver.get_stripe_client(scope="host")
        customer = await sc.v1.customers.create_async(params={
            "metadata": {
                "tenant_id": checkout_req.tenant_id
            },
            "email": checkout_req.email
        })
        
        checkout_session = await sc.v1.checkout.sessions.create_async(params={
            "mode": checkout_req.mode,
            "customer": customer.id,
            "line_items": [{
                "price": checkout_req.price_id,
                "quantity": 1
            }],
            "success_url": f"{frontend_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}&tenant_id={checkout_req.tenant_id}",
            "cancel_url": f"{frontend_url}/checkout/cancel?tenant_id={checkout_req.tenant_id}",
        })
        billing_record = BillingRecord(
            scope="host",
            actor="tenant",
            tenant_id=checkout_req.tenant_id,
            payment_type=checkout_req.mode,
            price_id=checkout_req.price_id,
            stripe_customer_id=customer.id,
            stripe_session_id=checkout_session.id,
            currency=checkout_session.currency if checkout_session.currency else "eur",
            status="pending",
        )
        await self.billing_record_repository.create(billing_record.model_dump())
        return checkout_session.url



    async def create_tenant_check_out_session_for_tenant_users(self, frontend_url: str, user_id: str, checkout_req: CheckoutRequestDto) -> str:
        """
        Create a Stripe checkout session for tenant scope for tenant's users
        """
        sc: StripeClient = await self.stripe_resolver.get_stripe_client(scope="tenant")
        customer = await sc.v1.customers.create_async(params={
            "email": checkout_req.email,
            "metadata":{
                "tenant_id": checkout_req.tenant_id,
                "user_id": user_id
            }
        })
        
        checkout_session = await sc.v1.checkout.sessions.create_async(params={
            "mode": checkout_req.mode,
            "customer": customer.id,
            "line_items": [{
                "price": checkout_req.price_id,
                "quantity": 1
            }],
            "success_url": f"{frontend_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}&user_id={user_id}",
            "cancel_url": f"{frontend_url}/checkout/cancel?user_id={user_id}",
        })

        billing_record = BillingRecord(
            scope="tenant",
            actor="end_user",
            tenant_id=checkout_req.tenant_id,
            user_id=user_id,
            payment_type=checkout_req.mode,
            price_id=checkout_req.price_id,
            stripe_customer_id=customer.id,
            stripe_session_id=checkout_session.id,
            currency=checkout_session.currency if checkout_session.currency else "eur",
            status="pending",
        )
    
        await self.billing_record_repository.create(billing_record.model_dump())
        return checkout_session.url



    async def handle_host_checkout_success(self, session_id: str, tenant_id: str) -> None:
        """
        Handle successful checkout for host scope
        """
        sc: StripeClient = await self.stripe_resolver.get_stripe_client(scope="host")
        session = await sc.v1.checkout.sessions.retrieve_async(session=session_id)
        if session.payment_status != "paid":
            raise BillingRecordException(f"Payment not completed for session {session_id}")

        billing_record = await self.billing_record_repository.single_or_none(session_id=session_id)
        if billing_record is None:
            raise BillingRecordNotFoundException(session_id)
        if billing_record.tenant_id != tenant_id:
            raise BillingRecordException(f"Tenant ID mismatch for the billing record {session_id}")

        billing_record.status = "succeeded"
        await self.billing_record_repository.update(billing_record.id, billing_record.model_dump())



    async def handle_host_checkout_canceled(self, tenant_id: str) -> None:
        """
        Handle cancelled checkout for host scope
        """
        billing_records = await self.billing_record_repository.search({"tenant_id": tenant_id, "status": "pending"})
        for record in billing_records:
            record.status = "canceled"
            await self.billing_record_repository.update(record.id, record.model_dump())



    async def handle_tenant_checkout_success(self, session_id: str, user_id: str) -> None:
        """
        Handle successful checkout for tenant scope
        """
        sc: StripeClient = await self.stripe_resolver.get_stripe_client(scope="tenant")
        session = await sc.v1.checkout.sessions.retrieve_async(session=session_id)
        if session.payment_status != "paid":
            raise BillingRecordException(f"Payment not completed for session {session_id}")

        billing_record = await self.billing_record_repository.single_or_none(session_id=session_id)
        if billing_record is None:
            raise BillingRecordNotFoundException(session_id)
        if str(billing_record.user_id) != user_id:
            raise BillingRecordException(f"User ID mismatch for the billing record {session_id}")

        billing_record.status = "succeeded"
        await self.billing_record_repository.update(billing_record.id, billing_record.model_dump())


    async def handle_tenant_checkout_canceled(self, user_id: str) -> None:
        """
        Handle cancelled checkout for tenant scope
        """
        billing_records = await self.billing_record_repository.list({"user_id": user_id, "status": "pending"})
        for record in billing_records:
            record.status = "canceled"
            await self.billing_record_repository.update(record.id, record.model_dump())


    async def list_checkout_records(self, skip: int = 0, limit: int = 100) -> BillingRecordListDto:
        """
            List checkout records
        """
        return await self.billing_record_repository.list(skip=skip, limit=limit)
