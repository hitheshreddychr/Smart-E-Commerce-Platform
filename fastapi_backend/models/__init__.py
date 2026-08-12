#this creates the FastAPI application and database tables

from fastapi import FastAPI

from database.connection import Base, engine
from models.cart import Cart
from models.product import Product
from models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Smart E-Commerce Platform API is running"}