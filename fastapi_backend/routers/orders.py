import os
from datetime import datetime, timedelta
from decimal import Decimal

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.cart import Cart
from models.order import Order, OrderItem
from models.payment import Payment
from models.return_request import ReturnRequest
from schemas.return_request import (ReturnRequestCreate, ReturnRequestResponse)
from models.product import Product
from models.user import User
from schemas.order import (OrderResponse, OrderStatusUpdate)
from utils.permissions import (admin_or_staff_required)
from schemas.payment import CheckoutResponse, PaymentResponse
from utils.email_service import send_email
from utils.notification_service import create_notification
from utils.permissions import customer_required
from routers.websocket import manager


load_dotenv()


STRIPE_SECRET_KEY = os.getenv(
    "STRIPE_SECRET_KEY"
)

STRIPE_CURRENCY = os.getenv(
    "STRIPE_CURRENCY",
    "inr"
)


if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# CHECKOUT
# POST /orders/checkout
# ============================================================

@router.post(
    "/checkout",
    response_model=CheckoutResponse
)
async def checkout(
    db: Session = Depends(get_db),
    current_user: dict = Depends(customer_required)
):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe is not configured. "
                "Set STRIPE_SECRET_KEY in the .env file."
            )
        )

    cart_items = (
        db.query(Cart)
        .filter(
            Cart.user_id == current_user["id"]
        )
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = Decimal("0.00")
    order_items_data = []

    for cart_item in cart_items:

        product = (
            db.query(Product)
            .filter(
                Product.id == cart_item.product_id
            )
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Product {cart_item.product_id} "
                    "not found"
                )
            )

        if cart_item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid quantity for "
                    f"{product.name}"
                )
            )

        if cart_item.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Insufficient stock for "
                    f"{product.name}. "
                    f"Available stock: {product.stock}, "
                    f"requested quantity: "
                    f"{cart_item.quantity}"
                )
            )

        item_price = Decimal(
            str(product.price)
        )

        item_total = (
            item_price * cart_item.quantity
        )

        total_amount += item_total

        order_items_data.append(
            {
                "product_id": product.id,
                "quantity": cart_item.quantity,
                "price": item_price
            }
        )

    # ========================================================
    # CREATE ORDER
    # ========================================================

    new_order = Order(
        user_id=current_user["id"],
        total_amount=total_amount,
        status="pending",
        payment_status="pending"
    )

    db.add(new_order)
    db.flush()

    # ========================================================
    # CREATE ORDER ITEMS
    # ========================================================

    for item in order_items_data:

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"]
        )

        db.add(order_item)

    # ========================================================
    # CREATE ORDER CONFIRMATION NOTIFICATION
    # ========================================================

    create_notification(
        db=db,
        user_id=current_user["id"],
        notification_type="order_confirmed",
        message=(
            f"Your order #{new_order.id} has been "
            "confirmed successfully."
        )
    )

    # ========================================================
    # REDUCE PRODUCT STOCK
    # ========================================================

    for cart_item in cart_items:

        product = (
            db.query(Product)
            .filter(
                Product.id == cart_item.product_id
            )
            .first()
        )

        if not product:
            db.rollback()

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        if cart_item.quantity > product.stock:
            db.rollback()

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Insufficient stock for "
                    f"{product.name}. "
                    f"Available stock: {product.stock}, "
                    f"requested quantity: "
                    f"{cart_item.quantity}"
                )
            )

        product.stock -= cart_item.quantity

    # ========================================================
    # CREATE PAYMENT RECORD
    # ========================================================

    payment = Payment(
        order_id=new_order.id,
        amount=total_amount,
        payment_method="stripe",
        status="pending"
    )

    db.add(payment)

    # ========================================================
    # GET USER FOR EMAIL
    # ========================================================

    user = (
        db.query(User)
        .filter(
            User.id == current_user["id"]
        )
        .first()
    )

    # ========================================================
    # STRIPE AMOUNT
    # ========================================================

    stripe_amount = int(
        total_amount * Decimal("100")
    )

    try:

        # ====================================================
        # STRIPE PAYMENT INTENT
        # ====================================================

        payment_intent = stripe.PaymentIntent.create(
            amount=stripe_amount,
            currency=STRIPE_CURRENCY,
            metadata={
                "order_id": str(new_order.id),
                "payment_id": str(payment.id),
                "user_id": str(current_user["id"])
            },
            automatic_payment_methods={
                "enabled": True
            }
        )

        payment.transaction_id = (
            payment_intent.id
        )

        payment.status = (
            payment_intent.status
        )

        # ====================================================
        # STRIPE CHECKOUT SESSION
        # ====================================================

        checkout_session = (
            stripe.checkout.Session.create(
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": (
                                STRIPE_CURRENCY
                            ),
                            "product_data": {
                                "name": (
                                    f"Order "
                                    f"#{new_order.id}"
                                )
                            },
                            "unit_amount": (
                                stripe_amount
                            )
                        },
                        "quantity": 1
                    }
                ],
                metadata={
                    "order_id": str(
                        new_order.id
                    ),
                    "payment_id": str(
                        payment.id
                    ),
                    "user_id": str(
                        current_user["id"]
                    )
                },
                payment_intent_data={
                    "metadata": {
                        "order_id": str(
                            new_order.id
                        ),
                        "payment_id": str(
                            payment.id
                        ),
                        "user_id": str(
                            current_user["id"]
                        )
                    }
                },
                success_url=(
                    "http://localhost:5173/"
                    "payment-success"
                    "?session_id="
                    "{CHECKOUT_SESSION_ID}"
                ),
                cancel_url=(
                    "http://localhost:5173/"
                    "payment-cancelled"
                )
            )
        )

        # ====================================================
        # SAVE DATABASE CHANGES
        # ====================================================

        db.commit()

        db.refresh(new_order)
        db.refresh(payment)

        # ====================================================
        # SEND REAL-TIME ORDER UPDATE
        # ====================================================

        await manager.send_personal_message(
            current_user["id"],
            {
                "event": "order_status_updated",
                "message": (
                    f"Order #{new_order.id} "
                    "has been created successfully"
                ),
                "order_id": new_order.id,
                "status": new_order.status,
                "payment_status": new_order.payment_status
            }
        )

        # ====================================================
        # SEND ORDER CONFIRMATION EMAIL
        # ====================================================

        if user:
            send_email(
                to_email=user.email,
                subject=(
                    "Order Confirmation - "
                    "Smart E-Commerce Platform"
                ),
                message=(
                    f"Hello {user.name},\n\n"
                    f"Your order #{new_order.id} "
                    "has been successfully created.\n\n"
                    f"Order Total: "
                    f"{total_amount} "
                    f"{STRIPE_CURRENCY.upper()}\n\n"
                    "Thank you for shopping with us!"
                )
            )

        return {
            "order_id": new_order.id,
            "amount": total_amount,
            "currency": STRIPE_CURRENCY,
            "payment_status": payment.status,
            "payment_intent_id": (
                payment_intent.id
            ),
            "payment_intent_client_secret": (
                payment_intent.client_secret
            ),
            "checkout_session_id": (
                checkout_session.id
            ),
            "checkout_url": (
                checkout_session.url
            )
        }

    except stripe.error.StripeError as exc:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=(
                "Stripe payment initialization failed: "
                f"{str(exc)}"
            )
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Checkout failed: {str(exc)}"
            )
        )


# ============================================================
# GET MY ORDERS
# GET /orders/
# ============================================================

@router.get(
    "/",
    response_model=list[OrderResponse]
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        customer_required
    )
):
    orders = (
        db.query(Order)
        .filter(
            Order.user_id == current_user["id"]
        )
        .all()
    )

    result = []

    for order in orders:

        order_items = (
            db.query(OrderItem)
            .filter(
                OrderItem.order_id == order.id
            )
            .all()
        )

        result.append(
            {
                "id": order.id,
                "user_id": order.user_id,
                "total_amount": order.total_amount,
                "status": order.status,
                "payment_status": (
                    order.payment_status
                ),
                "items": order_items
            }
        )

    return result


# ============================================================
# GET PAYMENT BY ORDER
# GET /orders/{order_id}/payment
# ============================================================

@router.get(
    "/{order_id}/payment",
    response_model=PaymentResponse
)
def get_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        customer_required
    )
):
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user["id"]
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    payment = (
        db.query(Payment)
        .filter(
            Payment.order_id == order_id
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment record not found"
        )

    return payment


# ============================================================
# UPDATE ORDER STATUS
# PUT /orders/{order_id}/status
# ============================================================

@router.put(
    "/{order_id}/status"
)
async def update_order_status(
    order_id: int,
    order_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        admin_or_staff_required
    )
):
    allowed_statuses = [
        "shipped",
        "delivered"
    ]

    if order_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Status must be either "
                "'shipped' or 'delivered'"
            )
        )

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    print(
        f"Order ID: {order.id}, "
        f"User ID: {order.user_id}"
    )

    print(
        f"Updating order #{order.id} "
        f"to status: {order_data.status}"
    )

    order.status = order_data.status

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

    if order_data.status == "shipped":

        create_notification(
            db=db,
            user_id=order.user_id,
            notification_type="order_shipped",
            message=(
                f"Your order #{order.id} "
                "has been shipped."
            )
        )

        email_subject = (
            "Order Shipped - "
            "Smart E-Commerce Platform"
        )

        email_message = (
            f"Hello {user.name},\n\n"
            f"Your order #{order.id} "
            "has been shipped.\n\n"
            "Your order is on the way!"
        )

    elif order_data.status == "delivered":

        create_notification(
            db=db,
            user_id=order.user_id,
            notification_type="order_delivered",
            message=(
                f"Your order #{order.id} "
                "has been delivered."
            )
        )

        email_subject = (
            "Order Delivered - "
            "Smart E-Commerce Platform"
        )

        email_message = (
            f"Hello {user.name},\n\n"
            f"Your order #{order.id} "
            "has been delivered.\n\n"
            "Thank you for shopping with us!"
        )

    db.commit()

    print(
        f"Order #{order.id} status successfully "
        f"updated to: {order.status}"
    )

    # ========================================================
    # SEND REAL-TIME WEBSOCKET UPDATE
    # ========================================================

    await manager.send_personal_message(
        order.user_id,
        {
            "event": "order_status_updated",
            "message": (
                f"Order #{order.id} status updated"
            ),
            "order_id": order.id,
            "status": order.status
        }
    )

    # ========================================================
    # SEND EMAIL
    # ========================================================

    print(
        f"Sending {order_data.status} email "
        f"to: {user.email}"
    )

    print(
        f"Email subject: {email_subject}"
    )

    send_email(
        to_email=user.email,
        subject=email_subject,
        message=email_message
    )

    print(
        f"{order_data.status.capitalize()} "
        f"email function executed successfully."
    )

    return {
        "message": (
            "Order status updated successfully"
        ),
        "order_id": order.id,
        "status": order.status
    }


# ============================================================
# REQUEST RETURN
# POST /orders/{order_id}/return
# ============================================================

@router.post(
    "/{order_id}/return",
    response_model=ReturnRequestResponse
)
def request_return(
    order_id: int,
    return_data: ReturnRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(customer_required)
):
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user["id"]
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status != "delivered":
        raise HTTPException(
            status_code=400,
            detail="Return can only be requested for delivered orders"
        )

    # ========================================================
    # RETURN WINDOW
    # ========================================================
    return_window_days = 7
    return_deadline = (
        order.created_at + timedelta(days=return_window_days)
    )

    if datetime.utcnow() > return_deadline:
        raise HTTPException(
            status_code=400,
            detail=(
                "Return window has expired. "
                "Returns can only be requested within 7 days "
                "of the order date."
            )
        )

    existing_request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.order_id == order_id,
            ReturnRequest.user_id == current_user["id"]
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Return request already exists for this order"
        )

    new_return_request = ReturnRequest(
        order_id=order.id,
        user_id=current_user["id"],
        reason=return_data.reason,
        comment=return_data.comment,
        status="pending"
    )

    db.add(new_return_request)

    order.status = "return_requested"

    db.commit()
    db.refresh(new_return_request)

    return new_return_request