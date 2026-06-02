import stripe
from core.config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_API_KEY


class BillingService:
    def __init__(self):
        self.price_id = settings.STRIPE_PRO_PRICE_ID

    def create_checkout_session(self, user_id: str, user_email: str) -> str:
        """
        Creates a Stripe Checkout Session for upgrading to Pro.
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": self.price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{settings.FRONTEND_URL}/settings?billing_success=true",
                cancel_url=f"{settings.FRONTEND_URL}/settings?billing_cancel=true",
                customer_email=user_email,
                metadata={
                    "user_id": user_id
                }
            )
            return session.url
        except Exception as e:
            raise ValueError(f"Stripe Checkout Session creation failed: {str(e)}")

    def create_portal_session(self, stripe_customer_id: str) -> str:
        """
        Creates a Stripe Billing Portal Session for users to manage their subscription.
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=stripe_customer_id,
                return_url=f"{settings.FRONTEND_URL}/settings"
            )
            return session.url
        except Exception as e:
            raise ValueError(f"Stripe Portal Session creation failed: {str(e)}")

    def construct_event(self, payload: bytes, sig_header: str) -> dict:
        """
        Constructs and verifies a Stripe webhook event.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f"Invalid webhook signature: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process webhook event: {str(e)}")
