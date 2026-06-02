from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import get_current_user
from models.user import User
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
    if user.plan == "pro":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already on the Pro plan."
        )
    try:
        checkout_url = billing_service.create_checkout_session(
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
    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found. Upgrade first."
        )
    try:
        portal_url = billing_service.create_portal_session(user.stripe_customer_id)
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
    """
    Handles Stripe webhooks (subscription lifecycle).
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    
    try:
        event = billing_service.construct_event(payload, sig_header)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})
    
    logger.info(f"Processing Stripe Webhook event: {event_type}")
    
    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        # Fetch subscription details
        stripe_customer_id = data_object.get("customer")
        stripe_sub_id = data_object.get("id")
        
        # User ID is stored in metadata or we search by email/customer ID
        user_id_str = data_object.get("metadata", {}).get("user_id")
        user = None
        
        if user_id_str:
            try:
                user_uuid = uuid.UUID(user_id_str)
                result = await db.execute(select(User).where(User.id == user_uuid))
                user = result.scalar_one_or_none()
            except Exception:
                pass
                
        if not user:
            # Fallback to customer ID lookup
            result = await db.execute(select(User).where(User.stripe_customer_id == stripe_customer_id))
            user = result.scalar_one_or_none()
            
        if not user:
            # Fallback to email lookup if we have it
            customer_email = data_object.get("customer_email")
            if customer_email:
                result = await db.execute(select(User).where(User.email == customer_email))
                user = result.scalar_one_or_none()
                
        if user:
            # Upgrade user plan to pro
            user.plan = "pro"
            user.stripe_customer_id = stripe_customer_id
            user.stripe_subscription_id = stripe_sub_id
            db.add(user)
            await db.commit()
            logger.info(f"User {user.email} successfully upgraded to Pro via webhook.")
            
    elif event_type == "customer.subscription.deleted":
        stripe_customer_id = data_object.get("customer")
        stripe_sub_id = data_object.get("id")
        
        result = await db.execute(
            select(User).where(User.stripe_subscription_id == stripe_sub_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            result = await db.execute(
                select(User).where(User.stripe_customer_id == stripe_customer_id)
            )
            user = result.scalar_one_or_none()
            
        if user:
            user.plan = "free"
            user.stripe_subscription_id = None
            db.add(user)
            await db.commit()
            logger.info(f"User {user.email} subscription cancelled. Plan downgraded to Free.")

    return {"status": "success"}
