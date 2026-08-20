from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from routers import auth
from routers import products
from routers import cart
from routers import users
from routers import orders
from routers import checkout
from routers.password import router as password_router
from routers import stripe_webhook


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

Assessment 5 features include checkout functionality,
Stripe payment integration, payment tracking, and order
payment status updates.
""",
    version="1.0.0",
    contact={
        "name": "Smart E-Commerce Platform"
    },
)


# -----------------------------------------
# CORS
# -----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------
# Session Middleware
# -----------------------------------------

app.add_middleware(
    SessionMiddleware,
    secret_key="smart-ecommerce-secret-key"
)


# -----------------------------------------
# Routers
# -----------------------------------------

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(checkout.router)
app.include_router(password_router)
app.include_router(stripe_webhook.router)


# -----------------------------------------
# Home
# -----------------------------------------

@app.get(
    "/",
    tags=["Home"],
    summary="API Status"
)
def home():
    return {
        "message": "Smart E-Commerce Platform API is running",
        "documentation": "/docs",
        "redoc": "/redoc"
    }