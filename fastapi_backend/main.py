from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from routers import auth
from routers import products
from routers import cart
from routers import users
from routers import orders
from routers.password import router as password_router


app = FastAPI(
    title="Smart E-Commerce Platform",
    version="1.0.0"
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
# Session middleware required for Auth0 OAuth
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
app.include_router(password_router)


# -----------------------------------------
# Home
# -----------------------------------------

@app.get("/")
def home():
    return {
        "message": "Smart E-Commerce Platform API is running"
    }