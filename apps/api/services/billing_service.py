import asyncio
import stripe
from core.config import settings


class BillingService:
    _available: bool

    def __init__(self):
        self._available = bool(settings.STRIPE_SECRET_KEY)
        if self._available:
            stripe.api_key = settings.STRIPE_SECRET_KEY
        self.price_id = settings.STRIPE_PRO_PRICE_ID

    @property
    def available(self) -> bool:
        return self._available

    async def create_checkout_session(self, user_id: str, user_email: str) -> str:
        try:
            session = await asyncio.to_thread(
                stripe.checkout.Session.create,
                line_items=[{"price": self.price_id, "quantity": 1}],
                mode="subscription",
                success_url=f"{settings.FRONTEND_URL}/settings?billing_success=true",
                cancel_url=f"{settings.FRONTEND_URL}/settings?billing_cancel=true",
                customer_email=user_email,
                metadata={"user_id": user_id},
            )
            return session.url
        except Exception as e:
            raise ValueError(f"Stripe Checkout Session creation failed: {str(e)}")

    async def create_portal_session(self, stripe_customer_id: str) -> str:
        try:
            session = await asyncio.to_thread(
                stripe.billing_portal.Session.create,
                customer=stripe_customer_id,
                return_url=f"{settings.FRONTEND_URL}/settings",
            )
            return session.url
        except Exception as e:
            raise ValueError(f"Stripe Portal Session creation failed: {str(e)}")

    def construct_event(self, payload: bytes, sig_header: str) -> dict:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return dict(event)
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f"Invalid webhook signature: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process webhook event: {str(e)}")
