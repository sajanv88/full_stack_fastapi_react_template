from typing import Any
import json

import stripe
from api.common.utils import get_logger
from api.core.container import (
    get_stripe_setting_service,
    get_billing_record_service
)
from api.usecases.stripe_setting_service import StripeSettingService
from api.usecases.billing_record_service import BillingRecordService
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks")
router.tags = ["Stripe"]

SUPPORTED_EVENTS = {
    "invoice.paid": lambda obj, svc: handle_invoice_paid(obj, svc),
}


@router.post("/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_setting_service: StripeSettingService = Depends(get_stripe_setting_service),
    billing_record_service: BillingRecordService = Depends(get_billing_record_service),
):
    event = None
    payload = await request.body()
    stripe_settings = await stripe_setting_service.get_stripe_secret()

    # If there is no Stripe settings. Return early
    if not stripe_settings or not stripe_settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not set on server",
        )
    
    try:
        sig_header = request.headers.get("stripe-signature")

        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=stripe_settings.stripe_webhook_secret,
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
        return JSONResponse(status_code=404, content={"message": "Unhandled event type"})

    await SUPPORTED_EVENTS.get(event_type, None)(data_object, billing_record_service)

    return JSONResponse(status_code=200, content={"status": "success"})


async def handle_invoice_paid(
    invoice: dict[str, Any],
    billing_record_service: BillingRecordService,
) -> None:
    tenant_id = invoice.get("metadata", {}).get("tenant_id")

    billing_dto = await billing_record_service.from_stripe_invoice_paid(
        invoice=invoice,
        scope="tenant",
        tenant_id=tenant_id
    )

    if not billing_dto:
        logger.warning(f"Could not convert invoice to BillingRecordDto: {invoice['id']}")
        return

    try:
        await billing_record_service.create_billing_record(billing_dto)
        logger.info(f"BillingRecord created for tenant {tenant_id} – invoice {invoice['id']}")
    except Exception as e:
        logger.exception(f"Failed to save BillingRecord for invoice {invoice['id']}: {e}")
