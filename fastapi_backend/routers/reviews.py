from fastapi import APIRouter, Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.order import Order, OrderItem
from models.product import Product
from models.review import Review
from utils.security import SECRET_KEY, ALGORITHM


router = APIRouter(
    tags=["Reviews"]
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
# GET CURRENT USER ID
# ============================================================

def get_current_user_id(request: Request) -> int:

    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    try:
        scheme, token = authorization.split(" ")

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme"
            )

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid access token"
            )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return int(user_id)

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header"
        )


# ============================================================
# CREATE REVIEW
# POST /reviews
# ============================================================

@router.post("/reviews")
def create_review(
    request: Request,
    product_id: int,
    rating: int,
    comment: str,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # GET LOGGED-IN USER
    # --------------------------------------------------------

    user_id = get_current_user_id(request)

    # --------------------------------------------------------
    # VALIDATE RATING
    # --------------------------------------------------------

    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )

    # --------------------------------------------------------
    # VALIDATE COMMENT
    # --------------------------------------------------------

    if not comment.strip():
        raise HTTPException(
            status_code=400,
            detail="Comment cannot be empty"
        )

    # --------------------------------------------------------
    # CHECK PRODUCT
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
    # CHECK COMPLETED ORDER
    # --------------------------------------------------------

    completed_order = (
        db.query(OrderItem)
        .join(
            Order,
            Order.id == OrderItem.order_id
        )
        .filter(
            Order.user_id == user_id,
            Order.status == "completed",
            OrderItem.product_id == product_id
        )
        .first()
    )

    if not completed_order:
        raise HTTPException(
            status_code=403,
            detail="You can review only products from completed orders"
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE REVIEW
    # --------------------------------------------------------

    existing_review = (
        db.query(Review)
        .filter(
            Review.user_id == user_id,
            Review.product_id == product_id
        )
        .first()
    )

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this product"
        )

    # --------------------------------------------------------
    # CREATE REVIEW
    # --------------------------------------------------------

    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=comment.strip(),
        status="pending"
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "message": "Review submitted successfully",
        "review": {
            "id": review.id,
            "user_id": review.user_id,
            "product_id": review.product_id,
            "rating": review.rating,
            "comment": review.comment,
            "status": review.status,
            "created_at": review.created_at
        }
    }


# ============================================================
# GET PRODUCT REVIEWS
# GET /products/{product_id}/reviews
# ============================================================

@router.get("/products/{product_id}/reviews")
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # CHECK PRODUCT
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
    # GET APPROVED REVIEWS
    # --------------------------------------------------------

    reviews = (
        db.query(Review)
        .filter(
            Review.product_id == product_id,
        )
        .order_by(
            Review.created_at.desc()
        )
        .all()
    )

    # --------------------------------------------------------
    # RATING AGGREGATION
    # --------------------------------------------------------

    aggregation = (
        db.query(
            func.avg(Review.rating),
            func.count(Review.id)
        )
        .filter(
            Review.product_id == product_id,
            Review.status == "approved"
        )
        .first()
    )

    average_rating = aggregation[0] or 0
    total_reviews = aggregation[1] or 0

    # --------------------------------------------------------
    # FORMAT REVIEWS
    # --------------------------------------------------------

    review_list = []

    for review in reviews:
        review_list.append(
            {
                "id": review.id,
                "user_id": review.user_id,
                "product_id": review.product_id,
                "rating": review.rating,
                "comment": review.comment,
                "status": review.status,
                "created_at": review.created_at
            }
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "product_id": product_id,
        "average_rating": round(float(average_rating), 2),
        "total_reviews": total_reviews,
        "reviews": review_list
    }