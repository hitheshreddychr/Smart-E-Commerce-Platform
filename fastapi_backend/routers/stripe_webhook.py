import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.cart import Cart
from models.order import Order
from models.payment import Payment
from models.user import User
from utils.email_service import send_email
from utils.notification_service import create_notification


load_dotenv()


STRIPE_SECRET_KEY = os.getenv(
    "STRIPE_SECRET_KEY",
    ""
)

STRIPE_WEBHOOK_SECRET = os.getenv(
    "STRIPE_WEBHOOK_SECRET",
    ""
)


if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


router = APIRouter(
    prefix="/webhook",
    tags=["Stripe Webhook"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def convert_stripe_object(data):
    if hasattr(data, "to_dict"):
        return data.to_dict()

    if isinstance(data, dict):
        return data

    return {}


def get_payment(
    db: Session,
    order_id: int,
    payment_id: str | None = None
):
    if payment_id:
        payment = (
            db.query(Payment)
            .filter(
                Payment.id == int(payment_id)
            )
            .first()
        )

        if payment:
            return payment

    return (
        db.query(Payment)
        .filter(
            Payment.order_id == order_id
        )
        .first()
    )


def get_user(
    db: Session,
    user_id: int
):
    return (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    payload = await request.body()

    signature = request.headers.get(
        "stripe-signature"
    )

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=503,
            detail=(
                "Stripe webhook secret "
                "is not configured"
            )
        )

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature"
        )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload"
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe webhook signature"
        )

    event_type = event["type"]

    stripe_object = convert_stripe_object(
        event["data"]["object"]
    )

    # =========================================================
    # CHECKOUT SESSION COMPLETED
    # =========================================================

    if event_type == "checkout.session.completed":

        checkout_session = stripe_object

        metadata = (
            checkout_session.get("metadata")
            or {}
        )

        order_id = metadata.get(
            "order_id"
        )

        payment_id = metadata.get(
            "payment_id"
        )

        if not order_id:
            return {
                "received": True,
                "event_type": event_type
            }

        order = (
            db.query(Order)
            .filter(
                Order.id == int(order_id)
            )
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        # =====================================================
        # PREVENT DUPLICATE PROCESSING
        # =====================================================

        if order.payment_status == "paid":
            return {
                "received": True,
                "event_type": event_type,
                "message": (
                    "Payment was already processed"
                )
            }

        # =====================================================
        # UPDATE ORDER
        # =====================================================

        order.payment_status = "paid"
        order.status = "completed"

        # =====================================================
        # UPDATE PAYMENT
        # =====================================================

        payment = get_payment(
            db=db,
            order_id=order.id,
            payment_id=payment_id
        )

        if payment:
            payment.status = "paid"

            payment_intent_id = (
                checkout_session.get(
                    "payment_intent"
                )
            )

            if payment_intent_id:
                payment.transaction_id = (
                    str(payment_intent_id)
                )

        # =====================================================
        # CREATE PAYMENT SUCCESS NOTIFICATION
        # =====================================================

        create_notification(
            db=db,
            user_id=order.user_id,
            notification_type="payment_successful",
            message=(
                f"Payment for order #{order.id} "
                "was successful."
            )
        )

        # =====================================================
        # GET USER AND SEND SUCCESS EMAIL
        # =====================================================

        user = get_user(
            db=db,
            user_id=order.user_id
        )

        # =====================================================
        # CLEAR USER CART
        # =====================================================

        db.query(Cart).filter(
            Cart.user_id == order.user_id
        ).delete(
            synchronize_session=False
        )

        # =====================================================
        # SAVE DATABASE CHANGES
        # =====================================================

        db.commit()

        # =====================================================
        # SEND PAYMENT SUCCESS EMAIL
        # =====================================================

        if user:
            send_email(
                to_email=user.email,
                subject=(
                    "Payment Successful - "
                    "Smart E-Commerce Platform"
                ),
                message=(
                    f"Hello {user.name},\n\n"
                    f"Your payment for order "
                    f"#{order.id} was successful.\n\n"
                    f"Order Total: "
                    f"{order.total_amount}\n\n"
                    "Thank you for shopping with us!"
                )
            )

        return {
            "received": True,
            "event_type": event_type,
            "message": (
                "Checkout payment processed "
                "successfully"
            )
        }

    # =========================================================
    # PAYMENT INTENT SUCCEEDED
    # =========================================================

    elif event_type == "payment_intent.succeeded":

        payment_intent = stripe_object

        metadata = (
            payment_intent.get("metadata")
            or {}
        )

        order_id = metadata.get(
            "order_id"
        )

        payment_id = metadata.get(
            "payment_id"
        )

        if order_id:

            order = (
                db.query(Order)
                .filter(
                    Order.id == int(order_id)
                )
                .first()
            )

            if order:

                payment = get_payment(
                    db=db,
                    order_id=order.id,
                    payment_id=payment_id
                )

                if payment:
                    payment.status = "paid"

                    payment.transaction_id = (
                        payment_intent.get("id")
                    )

                    db.commit()

        return {
            "received": True,
            "event_type": event_type
        }

    # =========================================================
    # PAYMENT INTENT FAILED
    # =========================================================

    elif event_type == "payment_intent.payment_failed":

        payment_intent = stripe_object

        metadata = (
            payment_intent.get("metadata")
            or {}
        )

        order_id = metadata.get(
            "order_id"
        )

        payment_id = metadata.get(
            "payment_id"
        )

        if order_id:

            order = (
                db.query(Order)
                .filter(
                    Order.id == int(order_id)
                )
                .first()
            )

            if order:

                payment = get_payment(
                    db=db,
                    order_id=order.id,
                    payment_id=payment_id
                )

                if payment:
                    payment.status = "failed"

                    payment.transaction_id = (
                        payment_intent.get("id")
                    )

                order.payment_status = "failed"
                order.status = "cancelled"

                # =============================================
                # CREATE PAYMENT FAILED NOTIFICATION
                # =============================================

                create_notification(
                    db=db,
                    user_id=order.user_id,
                    notification_type="payment_failed",
                    message=(
                        f"Payment for order #{order.id} "
                        "failed. Please try again."
                    )
                )

                user = get_user(
                    db=db,
                    user_id=order.user_id
                )

                db.commit()

                # =============================================
                # SEND PAYMENT FAILED EMAIL
                # =============================================

                if user:
                    send_email(
                        to_email=user.email,
                        subject=(
                            "Payment Failed - "
                            "Smart E-Commerce Platform"
                        ),
                        message=(
                            f"Hello {user.name},\n\n"
                            f"Unfortunately, your payment "
                            f"for order #{order.id} failed.\n\n"
                            "Please try again."
                        )
                    )

        return {
            "received": True,
            "event_type": event_type
        }

    # =========================================================
    # OTHER EVENTS
    # =========================================================

    return {
        "received": True,
        "event_type": event_type
    }