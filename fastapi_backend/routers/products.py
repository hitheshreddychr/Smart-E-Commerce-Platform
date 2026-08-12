from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.product import Product
from utils.permissions import admin_required, authenticated_required


router = APIRouter(
    prefix="/products",
    tags=["Products"]
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
# GET ALL PRODUCTS
# ============================================================

@router.get("/")
def get_products(
    db: Session = Depends(get_db)
):
    products = db.query(Product).all()

    return products


# ============================================================
# GET SINGLE PRODUCT
# ============================================================

@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
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

    return product


# ============================================================
# CREATE PRODUCT
# ADMIN ONLY
# ============================================================

@router.post("/")
def create_product(
    product_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

    product = Product(
        name=product_data.get("name"),
        description=product_data.get("description"),
        price=product_data.get("price"),
        stock=product_data.get("stock"),
        images=product_data.get("images")
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return {
        "message": "Product created successfully",
        "product": product
    }


# ============================================================
# UPDATE PRODUCT
# ADMIN ONLY
# ============================================================

@router.put("/{product_id}")
def update_product(
    product_id: int,
    product_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

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

    if "name" in product_data:
        product.name = product_data["name"]

    if "description" in product_data:
        product.description = product_data["description"]

    if "price" in product_data:
        product.price = product_data["price"]

    if "stock" in product_data:
        product.stock = product_data["stock"]

    if "images" in product_data:
        product.images = product_data["images"]

    db.commit()
    db.refresh(product)

    return {
        "message": "Product updated successfully",
        "product": product
    }


# ============================================================
# DELETE PRODUCT
# ADMIN ONLY
# ============================================================

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):

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

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }