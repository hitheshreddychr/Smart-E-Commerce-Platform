from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.product import Product
from schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from utils.permissions import admin_required


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# GET ALL PRODUCTS + FILTERS
# ============================================================

@router.get(
    "/",
    response_model=list[ProductResponse]
)
def get_products(
    category: str | None = Query(
        default=None,
        description="Filter products by category"
    ),
    min_price: Decimal | None = Query(
        default=None,
        ge=0,
        description="Minimum product price"
    ),
    max_price: Decimal | None = Query(
        default=None,
        ge=0,
        description="Maximum product price"
    ),
    min_popularity: int | None = Query(
        default=None,
        ge=0,
        description="Minimum popularity"
    ),
    in_stock: bool | None = Query(
        default=None,
        description="Filter by stock availability"
    ),
    sort_by: str = Query(
        default="id",
        description="Sort by id, price, or popularity"
    ),
    sort_order: str = Query(
        default="asc",
        description="Sort order: asc or desc"
    ),
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category:
        query = query.filter(
            Product.category.ilike(category)
        )

    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    if min_popularity is not None:
        query = query.filter(
            Product.popularity >= min_popularity
        )

    if in_stock is True:
        query = query.filter(
            Product.stock > 0
        )

    elif in_stock is False:
        query = query.filter(
            Product.stock <= 0
        )

    if sort_by == "price":
        sort_column = Product.price

    elif sort_by == "popularity":
        sort_column = Product.popularity

    else:
        sort_column = Product.id

    if sort_order.lower() == "desc":
        query = query.order_by(
            sort_column.desc()
        )
    else:
        query = query.order_by(
            sort_column.asc()
        )

    return query.all()


# ============================================================
# GET PRODUCTS BY CATEGORY
# ============================================================

@router.get(
    "/category/{category}",
    response_model=list[ProductResponse]
)
def get_products_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    products = (
        db.query(Product)
        .filter(Product.category.ilike(category))
        .all()
    )

    return products


# ============================================================
# GET SINGLE PRODUCT
# ============================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
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

@router.post(
    "/",
    response_model=ProductResponse
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        images=product_data.images,
        category=product_data.category,
        popularity=product_data.popularity
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# ============================================================
# UPDATE PRODUCT
# ADMIN ONLY
# ============================================================

@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
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

    update_data = product_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


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