import os
from decimal import Decimal

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.order import Order, OrderItem
from models.payment import Payment
from models.product import Product
from models.return_request import ReturnRequest
from models.user import User
from utils.email_service import send_email
from utils.notification_service import create_notification
from utils.permissions import admin_required


load_dotenv()


# ============================================================
# STRIPE CONFIGURATION
# ============================================================

STRIPE_SECRET_KEY = os.getenv(
    "STRIPE_SECRET_KEY",
    ""
)

STRIPE_DEMO_MODE = os.getenv(
    "STRIPE_DEMO_MODE",
    "false"
).lower() == "true"


if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/admin/returns",
    tags=["Admin Returns"]
)


# ============================================================
# DATABASE
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# GET ALL RETURN REQUESTS
# GET /admin/returns
# ============================================================

@router.get("")
def get_all_returns(
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_required)
):
    return_requests = (
        db.query(ReturnRequest)
        .order_by(
            ReturnRequest.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": return_request.id,
            "order_id": return_request.order_id,
            "user_id": return_request.user_id,
            "reason": return_request.reason,
            "comment": return_request.comment,
            "status": return_request.status,
            "created_at": return_request.created_at
        }
        for return_request in return_requests
    ]


# ============================================================
# APPROVE RETURN
# POST /admin/returns/{id}/approve
# ============================================================

@router.post(
    "/{return_id}/approve"
)
def approve_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_required)
):
    # ========================================================
    # FIND RETURN REQUEST
    # ========================================================

    return_request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.id == return_id
        )
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    # ========================================================
    # PREVENT DUPLICATE PROCESSING
    # ========================================================

    if return_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Return request has already been "
                f"processed. Current status: "
                f"{return_request.status}"
            )
        )

    # ========================================================
    # FIND ORDER
    # ========================================================

    order = (
        db.query(Order)
        .filter(
            Order.id == return_request.order_id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # ========================================================
    # FIND ORDER ITEMS
    # ========================================================

    order_items = (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id == order.id
        )
        .all()
    )

    if not order_items:
        raise HTTPException(
            status_code=404,
            detail="Order items not found"
        )

    # ========================================================
    # FIND USER
    # ========================================================

    user = (
        db.query(User)
        .filter(
            User.id == order.user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Order user not found"
        )

    # ========================================================
    # INCREASE PRODUCT STOCK
    # ========================================================

    for order_item in order_items:

        product = (
            db.query(Product)
            .filter(
                Product.id == order_item.product_id
            )
            .first()
        )

        if not product:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Product {order_item.product_id} "
                    "not found"
                )
            )

        product.stock += order_item.quantity

    # ========================================================
    # UPDATE RETURN STATUS
    # APPROVED → RETURNED
    # ========================================================

    return_request.status = "returned"

    # ========================================================
    # FIND PAYMENT
    # ========================================================

    payment = (
        db.query(Payment)
        .filter(
            Payment.order_id == order.id
        )
        .first()
    )

    if not payment:
        db.rollback()

        raise HTTPException(
            status_code=404,
            detail="Payment record not found"
        )

    # ========================================================
    # STRIPE REFUND
    # ========================================================

    if STRIPE_DEMO_MODE and not STRIPE_SECRET_KEY:

        payment.status = "refunded"
        order.payment_status = "refunded"

    else:

        if not STRIPE_SECRET_KEY:
            db.rollback()

            raise HTTPException(
                status_code=503,
                detail=(
                    "Stripe is not configured. "
                    "Set STRIPE_SECRET_KEY in the .env file "
                    "or enable STRIPE_DEMO_MODE."
                )
            )

        if payment.status != "paid":
            db.rollback()

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Payment cannot be refunded. "
                    f"Current payment status: "
                    f"{payment.status}"
                )
            )

        if not payment.transaction_id:
            db.rollback()

            raise HTTPException(
                status_code=400,
                detail="Stripe transaction ID not found"
            )

        try:

            # ====================================================
            # RETRIEVE CHECKOUT SESSION
            # ====================================================

            checkout_session = (
                stripe.checkout.Session.retrieve(
                    payment.transaction_id
                )
            )

            payment_intent_id = (
                checkout_session.payment_intent
            )

            if not payment_intent_id:

                db.rollback()

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Stripe PaymentIntent not found "
                        "for this payment"
                    )
                )

            # ====================================================
            # CREATE STRIPE REFUND
            # ====================================================

            refund = stripe.Refund.create(
                payment_intent=payment_intent_id
            )

            # ====================================================
            # VERIFY REFUND
            # ====================================================

            if refund.status != "succeeded":

                db.rollback()

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Stripe refund was not successful. "
                        f"Refund status: {refund.status}"
                    )
                )

            # ====================================================
            # UPDATE PAYMENT STATUS
            # ====================================================

            payment.status = "refunded"

            order.payment_status = "refunded"

        except stripe.error.StripeError as exc:

            db.rollback()

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Stripe refund failed: {str(exc)}"
                )
            )

    # ========================================================
    # UPDATE ORDER STATUS
    # ========================================================

    order.status = "returned"

    # ========================================================
    # CREATE IN-APP NOTIFICATION
    # ========================================================

    create_notification(
        db=db,
        user_id=order.user_id,
        notification_type="return_approved",
        message=(
            f"Your return request #{return_request.id} "
            f"for Order #{order.id} has been approved."
        )
    )

    # ========================================================
    # REFUND COMPLETED NOTIFICATION
    # ========================================================

    create_notification(
        db=db,
        user_id=order.user_id,
        notification_type="refund_completed",
        message=(
            f"Your refund for Order #{order.id} "
            "has been completed successfully."
        )
    )

    # ========================================================
    # RETURN STATUS → REFUNDED
    # ========================================================

    return_request.status = "refunded"

    # ========================================================
    # SAVE DATABASE CHANGES
    # ========================================================

    db.commit()

    db.refresh(return_request)
    db.refresh(order)
    db.refresh(payment)

    # ========================================================
    # EMAIL - RETURN APPROVED
    # ========================================================

    send_email(
        to_email=user.email,
        subject=(
            "Return Approved - "
            "Smart E-Commerce Platform"
        ),
        message=(
            f"Hello {user.name},\n\n"
            f"Your return request #{return_request.id} "
            f"for Order #{order.id} has been approved.\n\n"
            "The returned product stock has been updated "
            "and your refund has been processed.\n\n"
            "Thank you."
        )
    )

    # ========================================================
    # EMAIL - REFUND COMPLETED
    # ========================================================

    send_email(
        to_email=user.email,
        subject=(
            "Refund Completed - "
            "Smart E-Commerce Platform"
        ),
        message=(
            f"Hello {user.name},\n\n"
            f"Your refund for Order #{order.id} "
            "has been completed successfully.\n\n"
            f"Refund Amount: ₹{payment.amount}\n\n"
            "Thank you for shopping with us."
        )
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "message": (
            "Return approved and refund "
            "completed successfully"
        ),
        "return_id": return_request.id,
        "order_id": order.id,
        "return_status": return_request.status,
        "order_status": order.status,
        "payment_status": payment.status
    }


# ============================================================
# REJECT RETURN
# POST /admin/returns/{return_id}/reject
# ============================================================

@router.post(
    "/{return_id}/reject"
)
def reject_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_required)
):
    # ========================================================
    # FIND RETURN REQUEST
    # ========================================================

    return_request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.id == return_id
        )
        .first()
    )

    if not return_request:
        raise HTTPException(
            status_code=404,
            detail="Return request not found"
        )

    # ========================================================
    # PREVENT DUPLICATE PROCESSING
    # ========================================================

    if return_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Return request has already been "
                f"processed. Current status: "
                f"{return_request.status}"
            )
        )

    # ========================================================
    # FIND ORDER
    # ========================================================

    order = (
        db.query(Order)
        .filter(
            Order.id == return_request.order_id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # ========================================================
    # FIND USER
    # ========================================================

    user = (
        db.query(User)
        .filter(
            User.id == order.user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Order user not found"
        )

    # ========================================================
    # UPDATE RETURN STATUS
    # PENDING → REJECTED
    # ========================================================

    return_request.status = "rejected"

    # ========================================================
    # UPDATE ORDER STATUS
    # ========================================================

    order.status = "rejected"

    # ========================================================
    # CREATE IN-APP NOTIFICATION
    # ========================================================

    create_notification(
        db=db,
        user_id=order.user_id,
        notification_type="return_rejected",
        message=(
            f"Your return request #{return_request.id} "
            f"for Order #{order.id} has been rejected."
        )
    )

    # ========================================================
    # SAVE DATABASE CHANGES
    # ========================================================

    db.commit()

    db.refresh(return_request)
    db.refresh(order)

    # ========================================================
    # SEND EMAIL
    # ========================================================

    send_email(
        to_email=user.email,
        subject=(
            "Return Rejected - "
            "Smart E-Commerce Platform"
        ),
        message=(
            f"Hello {user.name},\n\n"
            f"Your return request #{return_request.id} "
            f"for Order #{order.id} has been rejected.\n\n"
            f"Reason provided for return: "
            f"{return_request.reason}\n\n"
            "If you have any questions, please contact "
            "customer support.\n\n"
            "Thank you."
        )
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "message": "Return rejected successfully",
        "return_id": return_request.id,
        "order_id": order.id,
        "return_status": return_request.status,
        "order_status": order.status
    }