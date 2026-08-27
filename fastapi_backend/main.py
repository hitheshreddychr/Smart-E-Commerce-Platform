from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from database.connection import Base, engine

from routers import auth
from routers import products
from routers import cart
from routers import users
from routers import orders
from routers import checkout
from routers import stripe_webhook
from routers import notifications
from routers import websocket

from routers.password import router as password_router

from models import user
from models import product
from models import cart as cart_model
from models import order
from models import payment
from models import notification


# ============================================================
# DATABASE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Smart E-Commerce Platform API",
    description="""
Smart E-Commerce Platform API.

This API provides functionality for:

- User authentication and management
- Product browsing and management
- Shopping cart operations
- Order creation and tracking
- Stripe payment integration
- Checkout processing
- Stripe webhook handling
- Password management
- User notifications
- Email notifications
- Real-time WebSocket updates

Assessment 6 features include notification management,
email notifications, real-time updates, and WebSocket support.
""",
    version="1.0.0",
    contact={
        "name": "Smart E-Commerce Platform"
    }
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# SESSION MIDDLEWARE
# ============================================================

app.add_middleware(
    SessionMiddleware,
    secret_key="smart-ecommerce-secret-key"
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth.router)

app.include_router(products.router)

app.include_router(cart.router)

app.include_router(users.router)

app.include_router(orders.router)

app.include_router(checkout.router)

app.include_router(password_router)

app.include_router(stripe_webhook.router)

app.include_router(notifications.router)

app.include_router(websocket.router)


# ============================================================
# HOME
# ============================================================

@app.get(
    "/",
    tags=["Home"],
    summary="API Status"
)
def home():

    return {
        "message": "Smart E-Commerce Platform API is running",
        "documentation": "/docs",
        "redoc": "/redoc",
        "websocket": "/ws/{user_id}"
    }