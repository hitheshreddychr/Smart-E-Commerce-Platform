from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.product import Product
from models.product_view import ProductView
from models.user import User


router = APIRouter(
    prefix="/products",
    tags=["Product Views"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# RECORD PRODUCT VIEW
# ============================================================

@router.post("/{product_id}/view")
def record_product_view(
    product_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # Check whether the user exists
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # Check whether the product exists
    # --------------------------------------------------------

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # --------------------------------------------------------
    # Create browsing history record
    # --------------------------------------------------------

    product_view = ProductView(
        user_id=user_id,
        product_id=product_id
    )

    db.add(product_view)

    # --------------------------------------------------------
    # Increase product popularity
    # --------------------------------------------------------

    product.popularity += 1

    db.commit()
    db.refresh(product_view)

    return {
        "message": "Product view recorded successfully",
        "user_id": user_id,
        "product_id": product_id,
        "view_id": product_view.id,
        "popularity": product.popularity
    }