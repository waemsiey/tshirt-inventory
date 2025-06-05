# models.py will define the Product model using SQLAlchemy ORM. This model will be used to interact with the database.

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

#  This created a table in the database with the name 'products' and defines the columns for the table.
class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    orders = relationship("Orders", back_populates="product")
    variants = relationship("Variants", back_populates="product" , cascade ="all, delete-orphan")

    
#A one to many relationship is established between Product and Variants, meaning that each product can have multiple variants.
class Variants(Base):
    __tablename__ = 'variants'

    variant_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    size = Column(String, nullable=True)
    color = Column(String, nullable=True)
    quantity = Column(Integer, default=0, nullable=False)
    price = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    product = relationship("Product", back_populates="variants")
    

class Orders(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    size = Column(String, nullable=True)
    color = Column(String, nullable=True)
    order_date = Column(DateTime, default=datetime.now, nullable=False)
    total_price = Column(Float, nullable=False)

    product = relationship("Product", back_populates="orders")

