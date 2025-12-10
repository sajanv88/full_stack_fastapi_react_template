from typing import Any

import stripe
from api.common.exceptions import InvalidOperationException
from api.common.utils import get_logger
from api.core.container import get_billing_record_service, get_stripe_setting_service
from api.domain.dtos.stripe_setting_dto import CreateStripeSettingDto, StripeSettingDto
from api.domain.enum.feature import Feature as FeatureEnum
from api.domain.enum.permission import Permission
from api.domain.security.feature_access_management import check_feature_access
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.billing_record_service import BillingRecordService
from api.usecases.stripe_setting_service import StripeSettingService
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from api.core.config import settings

router = APIRouter(
    prefix="/configurations",
    dependencies=[
        Depends(
            check_permissions_for_current_role(
                required_permissions=[Permission.MANAGE_PAYMENTS_SETTINGS]
            )
        ),
        Depends(check_feature_access(FeatureEnum.STRIPE)),
    ],
)
router.tags = ["Stripe"]


@router.post("/stripe", status_code=status.HTTP_201_CREATED)
async def configure_stripe_setting(
    configuration: CreateStripeSettingDto,
    current_user: CurrentUser,
    stripe_setting_service: StripeSettingService = Depends(get_stripe_setting_service),
):
    if not current_user.tenant_id:
        raise InvalidOperationException(
            "Tenant context is required to configure Stripe settings."
        )

    await stripe_setting_service.configure_stripe_settings(
        settings=configuration, tenant_id=str(current_user.tenant_id)
    )
    return status.HTTP_201_CREATED


@router.get("/stripe", response_model=StripeSettingDto, status_code=status.HTTP_200_OK)
async def get_stripe_settings(
    current_user: CurrentUser,
    stripe_setting_service: StripeSettingService = Depends(get_stripe_setting_service),
):
    if not current_user.tenant_id:
        raise InvalidOperationException(
            "Tenant context is required to get Stripe settings."
        )
    return await stripe_setting_service.get_stripe_settings()


logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks")
router.tags = ["Stripe"]

SUPPORTED_EVENTS = {
    "invoice.paid": lambda obj, svc: handle_invoice_paid(obj, svc),
}


@router.post("/webhooks", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_setting_service: StripeSettingService = Depends(get_stripe_setting_service),
    billing_record_service: BillingRecordService = Depends(get_billing_record_service),
):
    event = None
    stripe_webhook_secret = None
    payload = await request.body()
    stripe_settings = await stripe_setting_service.get_stripe_secret()

    # Check the request context for tenant or host. If tenant then get tenant webhook secret otherwise use host from env
    if request.state.tenant_id:
        # Tenant-scoped webhook
        if not stripe_settings or not stripe_settings.stripe_webhook_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Tenant webhook secret not configured",
            )
        stripe_webhook_secret = stripe_settings.stripe_webhook_secret
    else:
        # Host-scoped webhook
        stripe_webhook_secret = settings.stripe_webhook_secret

    try:
        sig_header = request.headers.get("stripe-signature")

        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=stripe_webhook_secret,
        )
    except ValueError:
        # Invalid payload
        logger.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Unexpected error constructing event: {e}")
        raise HTTPException(status_code=400, detail="Webhook error")

    # Extract the event type and object
    event_type = event["type"]
    data_object = event["data"]["object"]

    # ------------------------------------------------------------------
    # Handle relevant Stripe events
    # ------------------------------------------------------------------

    if event_type not in SUPPORTED_EVENTS:
        logger.error(f"Unhandled event type: {event_type}")
        return JSONResponse(
            status_code=404, content={"message": "Unhandled event type"}
        )

    await SUPPORTED_EVENTS.get(event_type, None)(data_object, billing_record_service)

    return JSONResponse(status_code=200, content={"status": "success"})


async def handle_invoice_paid(
    invoice: dict[str, Any],
    billing_record_service: BillingRecordService,
) -> None:
    tenant_id = invoice.get("metadata", {}).get("tenant_id")

    billing_record = await billing_record_service.from_stripe_invoice_paid(
        invoice=invoice, scope="tenant" if tenant_id else "host", tenant_id=tenant_id
    )

    if not billing_record:
        logger.warning(
            f"Could not convert invoice to BillingRecordDto: {invoice['id']}"
        )
        return

    try:
        await billing_record_service.create_billing_record(billing_record)
        logger.info(
            f"BillingRecord created for tenant {tenant_id} – invoice {invoice['id']}"
        )
    except Exception as e:
        logger.exception(
            f"Failed to save BillingRecord for invoice {invoice['id']}: {e}"
        )
