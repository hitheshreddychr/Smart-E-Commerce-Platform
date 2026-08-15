from sqlalchemy import Column, Integer, Numeric, String, Text

from database.connection import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    description = Column(Text, nullable=True)

    price = Column(Numeric(10, 2), nullable=False)

    stock = Column(Integer, default=0, nullable=False)

    images = Column(Text, nullable=True)

    category = Column(
        String(100),
        nullable=False,
        default="General",
        server_default="General"
    )

    popularity = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )