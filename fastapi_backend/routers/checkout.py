import os
import uuid
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
from utils.permissions import customer_required


load_dotenv()


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


router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("")
def checkout(
    db: Session = Depends(get_db),
    current_user: dict = Depends(customer_required)
):

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
                "name": product.name,
                "quantity": cart_item.quantity,
                "price": item_price
            }
        )

    new_order = Order(
        user_id=current_user["id"],
        total_amount=total_amount,
        status="pending",
        payment_status="pending"
    )

    db.add(new_order)
    db.flush()

    for item in order_items_data:

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"]
        )

        db.add(order_item)

    db.flush()

    payment = Payment(
        order_id=new_order.id,
        amount=total_amount,
        payment_method="stripe",
        transaction_id=None,
        status="pending"
    )

    db.add(payment)
    db.flush()

    if STRIPE_DEMO_MODE and not STRIPE_SECRET_KEY:

        demo_transaction_id = (
            f"demo_txn_{uuid.uuid4().hex[:16]}"
        )

        payment.transaction_id = (
            demo_transaction_id
        )

        payment.status = "pending"

        new_order.payment_status = "pending"
        new_order.status = "pending"

        db.commit()

        return {
            "message": (
                "Checkout created successfully "
                "in Stripe demo mode"
            ),
            "demo_mode": True,
            "order_id": new_order.id,
            "payment_id": payment.id,
            "amount": float(total_amount),
            "currency": "inr",
            "payment_method": "stripe",
            "payment_status": payment.status,
            "order_status": new_order.status,
            "transaction_id": payment.transaction_id,
            "checkout_url": (
                "http://localhost:5173/"
                "payment-demo"
                f"?order_id={new_order.id}"
            )
        }

    if not STRIPE_SECRET_KEY:

        db.rollback()

        raise HTTPException(
            status_code=503,
            detail=(
                "Stripe is not configured. "
                "Set STRIPE_SECRET_KEY in .env "
                "or enable STRIPE_DEMO_MODE."
            )
        )

    try:

        payment_intent = (
            stripe.PaymentIntent.create(
                amount=int(
                    total_amount * Decimal("100")
                ),
                currency="inr",
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
                }
            )
        )

        checkout_session = (
            stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=[
                    "card"
                ],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": item["name"]
                            },
                            "unit_amount": int(
                                item["price"]
                                * Decimal("100")
                            )
                        },
                        "quantity": item["quantity"]
                    }
                    for item in order_items_data
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

        payment.transaction_id = (
            checkout_session.id
        )

        db.commit()

        return {
            "message": (
                "Checkout session created successfully"
            ),
            "demo_mode": False,
            "order_id": new_order.id,
            "payment_id": payment.id,
            "amount": float(total_amount),
            "currency": "inr",
            "payment_method": "stripe",
            "payment_status": payment.status,
            "order_status": new_order.status,
            "payment_intent_id": (
                payment_intent.id
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
            status_code=400,
            detail=f"Stripe error: {str(exc)}"
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Checkout failed: {str(exc)}"
        )


@router.post("/confirm/{session_id}")
def confirm_payment(
    session_id: str,
    db: Session = Depends(get_db)
):

    try:

        checkout_session = (
            stripe.checkout.Session.retrieve(
                session_id
            )
        )

        checkout_session_data = (
            checkout_session.to_dict()
        )

        payment_status = checkout_session_data.get(
            "payment_status"
        )

        if payment_status != "paid":

            raise HTTPException(
                status_code=400,
                detail="Payment has not been completed yet"
            )

        session_metadata = (
            checkout_session_data.get("metadata") or {}
        )

        order_id = session_metadata.get(
            "order_id"
        )

        if not order_id:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Order ID not found "
                    "in payment session"
                )
            )

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

        if (
            order.payment_status == "paid"
            and order.status == "completed"
        ):

            return {
                "message": (
                    "Payment already confirmed"
                ),
                "order_id": order.id,
                "payment_status": (
                    order.payment_status
                ),
                "order_status": order.status
            }

        payment = (
            db.query(Payment)
            .filter(
                Payment.order_id == order.id
            )
            .first()
        )

        order_items = (
            db.query(OrderItem)
            .filter(
                OrderItem.order_id == order.id
            )
            .all()
        )

        for order_item in order_items:

            product = (
                db.query(Product)
                .filter(
                    Product.id
                    == order_item.product_id
                )
                .first()
            )

            if not product:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Product "
                        f"{order_item.product_id} "
                        "not found"
                    )
                )

            if product.stock < order_item.quantity:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Insufficient stock for "
                        f"{product.name}"
                    )
                )

            product.stock -= (
                order_item.quantity
            )

        order.payment_status = "paid"
        order.status = "completed"

        if payment:

            payment.status = "paid"

        db.query(Cart).filter(
            Cart.user_id == order.user_id
        ).delete(
            synchronize_session=False
        )

        db.commit()

        return {
            "message": (
                "Payment confirmed successfully"
            ),
            "order_id": order.id,
            "payment_status": (
                order.payment_status
            ),
            "order_status": order.status
        }

    except stripe.error.StripeError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(exc)}"
        )

    except HTTPException:

        db.rollback()
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Payment confirmation failed: "
                f"{str(exc)}"
            )
        )