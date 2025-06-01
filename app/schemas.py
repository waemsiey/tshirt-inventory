#Pydantic Models for Data Validation and Serialization

from pydantic import BaseModel, Field
from typing import Optional, List

#this ensures that the data we receive for creating a product is valid
#Variant Schema
class VariantBase(BaseModel):
    size: str = Field(default=None, max_length=50)
    color: str = Field(default=None, max_length=50)
    quantity: int = Field(default=0, ge=0)
    price: float = Field(default=0.0, ge=0.0)

class VariantCreate(VariantBase):
    pass

class Variant(VariantBase):
    variant_id: int
    class Config:
        orm_mode = True

#Product Schema
class ProductBase(BaseModel):
    name: str
    description: str = Field(default=None, max_length=500)
class ProductCreate(ProductBase):
    variants: List[VariantCreate]
class Product(ProductBase):
    product_id: int
    variants: List[Variant] = []
    class Config:
        orm_mode = True  

#Order Schema
class OrderBase(BaseModel):
    product_id: int
    color: str
    size: str
    quantity: int = Field(default=1, ge=0)
    total_price: float = Field(default=0.0, ge=0.0)

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
   order_id: int
   variant: Variant
   class Config:
          orm_mode = True 