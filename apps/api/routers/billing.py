from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import get_current_user
from models.user import User
from core.config import settings
from services.billing_service import BillingService
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)

billing_service = BillingService()


@router.post("/checkout")
async def billing_checkout(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Creates a Stripe Checkout Session for upgrading to Pro.
    """
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Stripe billing is not configured. Contact support to upgrade."
        )
    if user.plan == "pro":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already on the Pro plan."
        )
    try:
        checkout_url = await billing_service.create_checkout_session(
            user_id=str(user.id),
            user_email=user.email
        )
        return {"url": checkout_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/portal")
async def billing_portal(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Redirects user to Stripe Customer Portal to manage subscription.
    """
    if not billing_service.available:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Stripe billing is not configured. Contact support to manage your subscription."
        )
    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found. Upgrade first."
        )
    try:
        portal_url = await billing_service.create_portal_session(user.stripe_customer_id)
        return {"url": portal_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        event = billing_service.construct_event(payload, sig_header)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})
    # Reject test events in production
    if settings.ENVIRONMENT == "production" and not event.get("livemode", True):
        logger.warning("Ignoring test-mode webhook event in production")
        return {"status": "skipped", "reason": "livemode mismatch"}
    logger.info(f"Processing Stripe Webhook event: {event_type} (id={event.get('id')})")
    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        stripe_customer_id = data_object.get("customer")
        stripe_sub_id = data_object.get("id")
        user_id_str = data_object.get("metadata", {}).get("user_id")
        user = None
        if user_id_str:
            try:
                user_uuid = uuid.UUID(user_id_str)
                result = await db.execute(select(User).where(User.id == user_uuid))
                user = result.scalar_one_or_none()
            except (ValueError, AttributeError):
                pass
        if not user:
            result = await db.execute(select(User).where(User.stripe_customer_id == stripe_customer_id))
            user = result.scalar_one_or_none()
        if not user:
            customer_email = data_object.get("customer_email")
            if customer_email:
                result = await db.execute(select(User).where(User.email == customer_email))
                user = result.scalar_one_or_none()
        if user:
            if user.stripe_subscription_id == stripe_sub_id:
                logger.info(f"Duplicate webhook for user {user.email} — subscription already recorded")
            else:
                user.plan = "pro"
                user.stripe_customer_id = stripe_customer_id
                user.stripe_subscription_id = stripe_sub_id
                db.add(user)
                await db.commit()
                logger.info(f"User {user.email} upgraded to Pro via webhook.")
    elif event_type == "customer.subscription.deleted":
        stripe_customer_id = data_object.get("customer")
        stripe_sub_id = data_object.get("id")
        result = await db.execute(select(User).where(User.stripe_subscription_id == stripe_sub_id))
        user = result.scalar_one_or_none()
        if not user:
            result = await db.execute(select(User).where(User.stripe_customer_id == stripe_customer_id))
            user = result.scalar_one_or_none()
        if user:
            if user.stripe_subscription_id is None:
                logger.info(f"Duplicate cancellation webhook for user {user.email} — already processed")
            else:
                user.plan = "free"
                user.stripe_subscription_id = None
                db.add(user)
                await db.commit()
                logger.info(f"User {user.email} subscription cancelled.")
    return {"status": "success"}
