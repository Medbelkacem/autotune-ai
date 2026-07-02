from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.deps import CurrentUserDep

router = APIRouter()
_settings = get_settings()


class CheckoutRequest(BaseModel):
    plan: str  # 'pro' | 'workshop' | 'enterprise'
    seats: int = 1


class CheckoutSession(BaseModel):
    checkout_url: str


@router.post("/checkout", response_model=CheckoutSession)
async def checkout(payload: CheckoutRequest, user: CurrentUserDep) -> CheckoutSession:
    if not _settings.stripe_secret_key:
        # Stub for local dev — return a placeholder URL.
        return CheckoutSession(
            checkout_url=f"https://billing.local/checkout/{user.org_id}/{payload.plan}"
        )

    import stripe

    stripe.api_key = _settings.stripe_secret_key
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": _price_for_plan(payload.plan), "quantity": payload.seats}],
        success_url="https://app.autotune.ai/billing/success",
        cancel_url="https://app.autotune.ai/billing/cancel",
        client_reference_id=str(user.org_id),
    )
    return CheckoutSession(checkout_url=session.url)


def _price_for_plan(plan: str) -> str:
    return {
        "pro": "price_pro_monthly",
        "workshop": "price_workshop_monthly",
        "enterprise": "price_enterprise_monthly",
    }.get(plan, "price_pro_monthly")


@router.post("/webhook", status_code=status.HTTP_204_NO_CONTENT)
async def webhook(request: Request, stripe_signature: str = Header(default="")) -> None:
    if not _settings.stripe_webhook_secret:
        return
    payload = await request.body()
    import stripe

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, _settings.stripe_webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:  # type: ignore[attr-defined]
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"bad webhook: {e}") from e

    # Handle event types: customer.subscription.created/updated/deleted, invoice.paid
    _ = event  # actual handler omitted
