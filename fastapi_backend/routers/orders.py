# This handles checkout and orders for the logged-in user

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.cart import Cart
from models.order import Order, OrderItem
from models.product import Product
from schemas.order import OrderResponse
from utils.permissions import customer_required


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
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
# CHECKOUT
# CUSTOMER ONLY
# ============================================================

@router.post(
    "/checkout",
    response_model=OrderResponse
)
def checkout(
    db: Session = Depends(get_db),
    current_user: dict = Depends(customer_required)
):

    # --------------------------------------------------------
    # Get logged-in customer's cart
    # --------------------------------------------------------

    cart_items = (
        db.query(Cart)
        .filter(Cart.user_id == current_user["id"])
        .all()
    )

    # --------------------------------------------------------
    # Cart must not be empty
    # --------------------------------------------------------

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = Decimal("0.00")

    order_items_data = []

    # --------------------------------------------------------
    # Check stock and calculate total
    # --------------------------------------------------------

    for cart_item in cart_items:

        product = (
            db.query(Product)
            .filter(Product.id == cart_item.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {cart_item.product_id} not found"
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

        item_total = item_price * cart_item.quantity

        total_amount += item_total

        order_items_data.append({
            "product_id": product.id,
            "quantity": cart_item.quantity,
            "price": item_price
        })

    # ========================================================
    # CREATE ORDER
    # ========================================================

    new_order = Order(
        user_id=current_user["id"],
        total_amount=total_amount,
        status="pending"
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

        product.stock = product.stock - cart_item.quantity

    # ========================================================
    # CLEAR CART
    # ========================================================

    for cart_item in cart_items:
        db.delete(cart_item)

    # ========================================================
    # SAVE EVERYTHING
    # ========================================================

    db.commit()

    db.refresh(new_order)

    # ========================================================
    # GET ORDER ITEMS
    # ========================================================

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == new_order.id)
        .all()
    )

    # ========================================================
    # RETURN ORDER
    # ========================================================

    return {
        "id": new_order.id,
        "user_id": new_order.user_id,
        "total_amount": new_order.total_amount,
        "status": new_order.status,
        "items": order_items
    }


# ============================================================
# GET MY ORDERS
# CUSTOMER ONLY
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
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        result.append({
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "status": order.status,
            "items": order_items
        })

    return result