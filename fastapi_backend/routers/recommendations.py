from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.order import Order, OrderItem
from models.product import Product
from models.product_view import ProductView
from models.review import Review
from schemas.product import ProductResponse


router = APIRouter(
    tags=["Recommendations"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_product_rating(
    db: Session,
    product_id: int
):
    rating = (
        db.query(
            func.avg(Review.rating)
        )
        .filter(
            Review.product_id == product_id,
            Review.status == "approved"
        )
        .scalar()
    )

    if rating is None:
        return 0.0

    return float(rating)


def get_product_view_count(
    db: Session,
    product_id: int
):
    view_count = (
        db.query(
            func.count(ProductView.id)
        )
        .filter(
            ProductView.product_id == product_id
        )
        .scalar()
    )

    return int(view_count or 0)


def get_user_viewed_product_ids(
    db: Session,
    user_id: int
):
    rows = (
        db.query(ProductView.product_id)
        .filter(
            ProductView.user_id == user_id
        )
        .order_by(
            ProductView.viewed_at.desc()
        )
        .all()
    )

    return [row[0] for row in rows]


def get_user_purchased_product_ids(
    db: Session,
    user_id: int
):
    rows = (
        db.query(OrderItem.product_id)
        .join(
            Order,
            OrderItem.order_id == Order.id
        )
        .filter(
            Order.user_id == user_id
        )
        .all()
    )

    return list(
        {
            row[0]
            for row in rows
        }
    )


def get_user_preference_categories(
    db: Session,
    user_id: int
):
    viewed_categories = (
        db.query(Product.category)
        .join(
            ProductView,
            ProductView.product_id == Product.id
        )
        .filter(
            ProductView.user_id == user_id
        )
        .all()
    )

    purchased_categories = (
        db.query(Product.category)
        .join(
            OrderItem,
            OrderItem.product_id == Product.id
        )
        .join(
            Order,
            OrderItem.order_id == Order.id
        )
        .filter(
            Order.user_id == user_id
        )
        .all()
    )

    categories = []

    for row in viewed_categories:
        categories.append(row[0])

    for row in purchased_categories:
        categories.append(row[0])

    return Counter(categories)


# ============================================================
# RECOMMENDED FOR USER
# ============================================================

@router.get(
    "/recommendations/{user_id}",
    response_model=list[ProductResponse]
)
def get_recommendations(
    user_id: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=50
    ),
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # Check whether user exists
    # --------------------------------------------------------

    from models.user import User

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
    # Get user activity
    # --------------------------------------------------------

    viewed_product_ids = set(
        get_user_viewed_product_ids(
            db,
            user_id
        )
    )

    purchased_product_ids = set(
        get_user_purchased_product_ids(
            db,
            user_id
        )
    )

    category_preferences = (
        get_user_preference_categories(
            db,
            user_id
        )
    )

    # --------------------------------------------------------
    # Get candidate products
    # --------------------------------------------------------

    products = (
        db.query(Product)
        .filter(
            Product.stock > 0
        )
        .all()
    )

    scored_products = []

    for product in products:

        # Do not recommend products already purchased.
        if product.id in purchased_product_ids:
            continue

        score = 0.0

        # ----------------------------------------------------
        # Browsing-history preference
        # ----------------------------------------------------

        if product.category in category_preferences:
            score += (
                category_preferences[
                    product.category
                ] * 10
            )

        # ----------------------------------------------------
        # Product popularity
        # ----------------------------------------------------

        score += (
            float(product.popularity or 0) * 0.5
        )

        # ----------------------------------------------------
        # Actual product view count
        # ----------------------------------------------------

        view_count = get_product_view_count(
            db,
            product.id
        )

        score += view_count * 1.5

        # ----------------------------------------------------
        # Product rating
        # ----------------------------------------------------

        average_rating = get_product_rating(
            db,
            product.id
        )

        score += average_rating * 5

        # ----------------------------------------------------
        # Recently viewed products get extra weight.
        # ----------------------------------------------------

        if product.id in viewed_product_ids:
            score += 5

        scored_products.append(
            (
                product,
                score
            )
        )

    # --------------------------------------------------------
    # Sort by recommendation score
    # --------------------------------------------------------

    scored_products.sort(
        key=lambda item: item[1],
        reverse=True
    )

    recommendations = [
        item[0]
        for item in scored_products[:limit]
    ]

    # --------------------------------------------------------
    # Fallback for users with no activity
    # --------------------------------------------------------

    if not recommendations:

        recommendations = (
            db.query(Product)
            .filter(
                Product.stock > 0
            )
            .order_by(
                Product.popularity.desc(),
                Product.id.desc()
            )
            .limit(limit)
            .all()
        )

    return recommendations


# ============================================================
# SIMILAR PRODUCTS
# ============================================================

@router.get(
    "/products/{product_id}/similar",
    response_model=list[ProductResponse]
)
def get_similar_products(
    product_id: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=50
    ),
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # Find original product
    # --------------------------------------------------------

    product = (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # --------------------------------------------------------
    # Find products from the same category
    # --------------------------------------------------------

    similar_products = (
        db.query(Product)
        .filter(
            Product.category == product.category,
            Product.id != product_id,
            Product.stock > 0
        )
        .order_by(
            Product.popularity.desc(),
            Product.id.desc()
        )
        .limit(limit)
        .all()
    )

    return similar_products


# ============================================================
# TRENDING PRODUCTS
# ============================================================

@router.get(
    "/products/trending",
    response_model=list[ProductResponse]
)
def get_trending_products(
    limit: int = Query(
        default=10,
        ge=1,
        le=50
    ),
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # Get view counts for every product
    # --------------------------------------------------------

    view_counts = (
        db.query(
            ProductView.product_id,
            func.count(ProductView.id).label(
                "view_count"
            )
        )
        .group_by(
            ProductView.product_id
        )
        .subquery()
    )

    # --------------------------------------------------------
    # Get average ratings for every product
    # --------------------------------------------------------

    average_ratings = (
        db.query(
            Review.product_id,
            func.avg(Review.rating).label(
                "average_rating"
            )
        )
        .filter(
            Review.status == "approved"
        )
        .group_by(
            Review.product_id
        )
        .subquery()
    )

    # --------------------------------------------------------
    # Combine popularity, views and ratings
    # --------------------------------------------------------

    products = (
        db.query(Product)
        .outerjoin(
            view_counts,
            Product.id == view_counts.c.product_id
        )
        .outerjoin(
            average_ratings,
            Product.id == average_ratings.c.product_id
        )
        .filter(
            Product.stock > 0
        )
        .order_by(
            (
                func.coalesce(
                    view_counts.c.view_count,
                    0
                ) * 3
                +
                func.coalesce(
                    average_ratings.c.average_rating,
                    0
                ) * 5
                +
                Product.popularity * 0.5
            ).desc()
        )
        .limit(limit)
        .all()
    )

    # --------------------------------------------------------
    # Fallback when there are no product views/reviews
    # --------------------------------------------------------

    if not products:

        products = (
            db.query(Product)
            .filter(
                Product.stock > 0
            )
            .order_by(
                Product.popularity.desc(),
                Product.id.desc()
            )
            .limit(limit)
            .all()
        )

    return products