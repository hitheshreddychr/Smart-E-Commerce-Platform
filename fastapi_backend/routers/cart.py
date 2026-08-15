from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.cart import Cart
from models.product import Product
from schemas.cart import (
    CartCreate,
    CartRemove,
    CartResponse,
    CartUpdate,
)
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


TAX_RATE = Decimal("0.00")


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def build_cart_response(
    db: Session,
    user_id: int
):
    cart_items = (
        db.query(Cart)
        .join(Product, Cart.product_id == Product.id)
        .filter(Cart.user_id == user_id)
        .all()
    )

    items = []
    cart_total = Decimal("0.00")

    for cart_item in cart_items:
        product = (
            db.query(Product)
            .filter(Product.id == cart_item.product_id)
            .first()
        )

        if not product:
            continue

        item_total = (
            Decimal(str(product.price))
            * cart_item.quantity
        )

        cart_total += item_total

        items.append(
            {
                "id": cart_item.id,
                "user_id": cart_item.user_id,
                "product_id": cart_item.product_id,
                "product_name": product.name,
                "price": Decimal(str(product.price)),
                "quantity": cart_item.quantity,
                "item_total": item_total,
                "stock": product.stock
            }
        )

    tax = cart_total * TAX_RATE
    grand_total = cart_total + tax

    return {
        "items": items,
        "cart_total": cart_total,
        "tax": tax,
        "grand_total": grand_total
    }


# ============================================================
# ADD PRODUCT TO CART
# POST /cart/add
# ============================================================

@router.post(
    "/add",
    response_model=CartResponse
)
def add_to_cart(
    cart_data: CartCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    product = (
        db.query(Product)
        .filter(Product.id == cart_data.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product.stock <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"{product.name} is out of stock"
        )

    existing_cart = (
        db.query(Cart)
        .filter(
            Cart.user_id == current_user["id"],
            Cart.product_id == cart_data.product_id
        )
        .first()
    )

    if existing_cart:
        new_quantity = (
            existing_cart.quantity
            + cart_data.quantity
        )

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Only {product.stock} units of "
                    f"{product.name} are available"
                )
            )

        existing_cart.quantity = new_quantity

    else:
        if cart_data.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Only {product.stock} units of "
                    f"{product.name} are available"
                )
            )

        new_cart = Cart(
            user_id=current_user["id"],
            product_id=cart_data.product_id,
            quantity=cart_data.quantity
        )

        db.add(new_cart)

    db.commit()

    return build_cart_response(
        db,
        current_user["id"]
    )


# ============================================================
# UPDATE CART QUANTITY
# PUT /cart/update
# ============================================================

@router.put(
    "/update",
    response_model=CartResponse
)
def update_cart(
    cart_data: CartUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    cart_item = (
        db.query(Cart)
        .filter(
            Cart.user_id == current_user["id"],
            Cart.product_id == cart_data.product_id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Product is not in your cart"
        )

    product = (
        db.query(Product)
        .filter(Product.id == cart_data.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if cart_data.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only {product.stock} units of "
                f"{product.name} are available"
            )
        )

    cart_item.quantity = cart_data.quantity

    db.commit()

    return build_cart_response(
        db,
        current_user["id"]
    )


# ============================================================
# REMOVE PRODUCT FROM CART
# DELETE /cart/remove
# ============================================================

@router.delete(
    "/remove",
    response_model=CartResponse
)
def remove_from_cart(
    cart_data: CartRemove,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cart_item = (
        db.query(Cart)
        .filter(
            Cart.user_id == current_user["id"],
            Cart.product_id == cart_data.product_id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Product is not in your cart"
        )

    db.delete(cart_item)
    db.commit()

    return build_cart_response(
        db,
        current_user["id"]
    )


# ============================================================
# VIEW CART
# GET /cart
# ============================================================

@router.get(
    "",
    response_model=CartResponse
)
def get_cart(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return build_cart_response(
        db,
        current_user["id"]
    )