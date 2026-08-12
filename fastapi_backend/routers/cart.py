# This handles the cart for the logged-in user

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.cart import Cart
from models.product import Product
from schemas.cart import CartCreate, CartResponse
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
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
# ADD TO CART
# ============================================================

@router.post(
    "/",
    response_model=CartResponse
)
def add_to_cart(
    cart: CartCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Quantity must be greater than zero
    # --------------------------------------------------------

    if cart.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    # --------------------------------------------------------
    # Find product
    # --------------------------------------------------------

    product = (
        db.query(Product)
        .filter(Product.id == cart.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # --------------------------------------------------------
    # Check stock
    # --------------------------------------------------------

    if product.stock <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"{product.name} is out of stock"
        )

    # --------------------------------------------------------
    # Check whether this product is already in cart
    # --------------------------------------------------------

    existing_cart = (
        db.query(Cart)
        .filter(
            Cart.user_id == current_user["id"],
            Cart.product_id == cart.product_id
        )
        .first()
    )

    # --------------------------------------------------------
    # If product already exists in cart,
    # add the new quantity to the existing quantity
    # --------------------------------------------------------

    if existing_cart:

        new_quantity = existing_cart.quantity + cart.quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Only {product.stock} units of "
                    f"{product.name} are available. "
                    f"You already have {existing_cart.quantity} "
                    f"in your cart."
                )
            )

        existing_cart.quantity = new_quantity

        db.commit()
        db.refresh(existing_cart)

        return existing_cart

    # --------------------------------------------------------
    # First time adding this product
    # --------------------------------------------------------

    if cart.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only {product.stock} units of "
                f"{product.name} are available"
            )
        )

    # --------------------------------------------------------
    # Create cart item
    # --------------------------------------------------------

    new_cart = Cart(
        user_id=current_user["id"],
        product_id=cart.product_id,
        quantity=cart.quantity
    )

    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    return new_cart


# ============================================================
# GET CART
# ============================================================

@router.get(
    "/",
    response_model=list[CartResponse]
)
def get_cart(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    return (
        db.query(Cart)
        .filter(Cart.user_id == current_user["id"])
        .all()
    )