import os
from decimal import Decimal

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.cart import Cart
from models.order import Order, OrderItem
from models.payment import Payment
from models.product import Product
from schemas.order import OrderResponse
from schemas.payment import CheckoutResponse, PaymentResponse
from utils.permissions import customer_required


load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_CURRENCY = os.getenv("STRIPE_CURRENCY", "inr")

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
def checkout(
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
        .filter(Cart.user_id == current_user["id"])
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
            .filter(Product.id == cart_item.product_id)
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
                detail=f"Invalid quantity for {product.name}"
            )

        if cart_item.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Insufficient stock for {product.name}. "
                    f"Available stock: {product.stock}, "
                    f"requested quantity: {cart_item.quantity}"
                )
            )

        item_price = Decimal(str(product.price))

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
    # REDUCE PRODUCT STOCK
    # ========================================================

    for cart_item in cart_items:

        product = (
            db.query(Product)
            .filter(Product.id == cart_item.product_id)
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
                    f"Insufficient stock for {product.name}. "
                    f"Available stock: {product.stock}, "
                    f"requested quantity: {cart_item.quantity}"
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
                "user_id": str(current_user["id"])
            },
            automatic_payment_methods={
                "enabled": True
            }
        )

        payment.transaction_id = payment_intent.id
        payment.status = payment_intent.status

        # ====================================================
        # STRIPE CHECKOUT SESSION
        # ====================================================

        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": STRIPE_CURRENCY,
                        "product_data": {
                            "name": f"Order #{new_order.id}"
                        },
                        "unit_amount": stripe_amount
                    },
                    "quantity": 1
                }
            ],
            metadata={
                "order_id": str(new_order.id),
                "user_id": str(current_user["id"])
            },
            success_url=(
                "http://localhost:5173/payment-success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=(
                "http://localhost:5173/payment-cancelled"
            )
        )

        # ====================================================
        # SAVE DATABASE
        # ====================================================

        db.commit()
        db.refresh(new_order)
        db.refresh(payment)

        return {
            "order_id": new_order.id,
            "amount": total_amount,
            "currency": STRIPE_CURRENCY,
            "payment_status": payment.status,
            "payment_intent_id": payment_intent.id,
            "payment_intent_client_secret": (
                payment_intent.client_secret
            ),
            "checkout_session_id": checkout_session.id,
            "checkout_url": checkout_session.url
        }

    except stripe.error.StripeError as exc:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=f"Stripe payment initialization failed: {str(exc)}"
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Checkout failed: {str(exc)}"
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
    current_user: dict = Depends(customer_required)
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user["id"])
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
                "payment_status": order.payment_status,
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

    payment = (
        db.query(Payment)
        .filter(Payment.order_id == order_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment record not found"
        )

    return payment