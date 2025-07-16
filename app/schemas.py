from pydantic import BaseModel, Field, root_validator, validator
from typing import Optional, List
from datetime import datetime

# Variant Schemas (unchanged)
class VariantBase(BaseModel):
    size: Optional[str] = None
    quantity: int = Field(default=0, ge=0)
    selling_price: float = Field(ge=0.0)
    item_cost: float = Field(ge=0.0)

class VariantCreate(VariantBase):
    pass

class Variant(VariantBase):
    variant_id: int
    product_id: int
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Product Schemas (unchanged)
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    image_url: str

class ProductCreate(ProductBase):
    variants: List[VariantCreate] = []

class Product(ProductBase):
    product_id: int
    created_at: datetime
    variants: List[Variant] = []
    
    class Config:
        orm_mode = True

# Service Schemas (unchanged)
class ServiceBase(BaseModel):
    name: str
    size: Optional[str] = None
    print_price: float = Field(ge=0.0)
    image_url: str

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    service_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


class OrderItemCreate(BaseModel):
    product_id: Optional[int] = Field(
        None,
        description="Required if not a service"
    )
    service_id: Optional[int] = Field(
        None,
        description="Required if not a product"
    )
    variant_id: Optional[int] = Field(
        None,
        description="Requires product_id"
    )
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

    @root_validator(pre=True)
    def validate_item(cls, values):
        # Ensure either product OR service is specified
        has_product = values.get('product_id') is not None
        has_service = values.get('service_id') is not None
        
        if not has_product and not has_service:
            raise ValueError("Item must specify product_id or service_id")
        if has_product and has_service:
            raise ValueError("Item cannot be both product and service")
        
        # Validate variant belongs to product
        if values.get('variant_id') and not has_product:
            raise ValueError("Variant requires product_id")
            
        return values

class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_items=1)
    discount: float = Field(0.0, ge=0)
    total_price: float = Field(..., ge=0)

    @validator('total_price')
    def validate_total(cls, v, values):
        items = values.get('items', [])
        discount = values.get('discount', 0)
        
        calculated = sum(
            item.price * item.quantity 
            for item in items
        ) - discount
        
        if abs(v - calculated) > 0.01:
            raise ValueError(
                f"Price mismatch. Expected: {calculated:.2f}\n"
                f"Calculation: sum({[i.price*i.quantity for i in items]}) - {discount} = {calculated}"
            )
        return v
    
class OrderItemBase(BaseModel):
    product_id: Optional[int] = Field(
        None,
        description="Required if not a service"
    )
    service_id: Optional[int] = Field(
        None,
        description="Required if not a product"
    )
    variant_id: Optional[int] = Field(
        None,
        description="Requires product_id"
    )
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    @validator('variant_id')
    def validate_variant(cls, v, values):
        if v and not values.get('product_id'):
            raise ValueError("Variant requires product_id")
        return v
class OrderItemDB(BaseModel):
    order_item_id: int
    order_id: int
    product_id: Optional[int] = None
    service_id: Optional[int] = None
    variant_id: Optional[int] = None
    quantity: int
    price: float

class OrderDB(BaseModel):
    order_id: int
    order_date: datetime
    total_price: float
    payment_status: Optional[str] = None# e.g., 'pending', 'paid', 'cancelled'
    items: List[OrderItemDB] = []
    payments: Optional[List['OrderPaymentResponse']] = None  # List of OrderPaymentResponse
    
    class Config:
        orm_mode = True


#Response Schemas

class OrderItemResponse(BaseModel):
    order_item_id: int
    order_id: int
    product_id: Optional[int]
    service_id: Optional[int] 
    variant_id: Optional[int] 
    quantity: int
    price: float

    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    order_id: int
    order_date: datetime
    total_price: float
    payment_status: Optional[str] = None
    items: List[OrderItemResponse]
    payments: Optional[List['OrderPaymentResponse']] = None 

    class Config:
        orm_mode = True


#order payment schemas

class OrderPaymentBase(BaseModel):
    order_id: int
    amount: float
    payment_date: Optional[datetime] = None
    status: str = "completed"

    class Config:
        orm_mode = True


class OrderPaymentCreate(OrderPaymentBase):
    pass

class OrderPaymentRead(OrderPaymentBase):
    payment_id: int
    created_at: datetime
    updated_at: datetime

#sales record schemas
class SalesRecordBase(BaseModel):
    date: Optional[datetime] = None
    total_sales: float
    closing_cash: float = 0.0
    opening_cash: float = 500.0
    trasaction_count: int = 0  # Keep your model's typo if already used
    remit_amount: float = 0.0
    remarks: Optional[str] = None

    class Config:
        orm_mode = True

class SalesRecordCreate(SalesRecordBase):
    cashout_transaction_id: Optional[int] = None

class SalesRecordRead(SalesRecordBase):
    record_id: int
    created_at: datetime
    cashout_transaction_id: Optional[int]

#cashout transaction schemas
class CashoutTransactionBase(BaseModel):
    amount: float
    reason: str
    cashout_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class CashoutTransactionCreate(CashoutTransactionBase):
    pass


class CashoutTransactionRead(CashoutTransactionBase):
    cashout_id: int
    created_at: datetime

class OrderPaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    payment_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TotalPaymentsResponse(BaseModel):
    total_payments: float

class ServicePaymentResponse(BaseModel):
    service_id: int
    name: str
    total_payments: float    
    class Config:
        orm_mode = True

class ProductPaymentResponse(BaseModel):
    product_id: int
    total_payments: float

    class Config:
        orm_mode = True
        
OrderResponse.update_forward_refs()
OrderDB.update_forward_refs()