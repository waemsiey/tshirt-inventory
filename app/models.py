from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    color = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    image_url = Column(String, nullable=False)

    variants = relationship("Variant", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")

class Variant(Base):
    __tablename__ = 'variants'

    variant_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    size = Column(String, nullable=True)
    quantity = Column(Integer, default=0, nullable=False)
    selling_price = Column(Float, nullable=False)
    item_cost = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    product = relationship("Product", back_populates="variants")
    order_items = relationship("OrderItem", back_populates="variant")

class Service(Base):
    __tablename__ = 'services'

    service_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    size = Column(String, nullable=True)
    print_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    image_url = Column(String, nullable=False)

    order_items = relationship("OrderItem", back_populates="service")

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime, default=datetime.now, nullable=False)
    total_price = Column(Float)
    payment_status = Column(String, default='pending', nullable=False)  # e.g., 'pending', 'paid', 'cancelled'

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("OrderPayment", back_populates="order", cascade="all, delete-orphan")
    



class OrderItem(Base):
    __tablename__ = 'order_items'
    __table_args__ = (
        CheckConstraint(
            '(product_id IS NOT NULL AND service_id IS NULL) OR '
            '(product_id IS NULL AND service_id IS NOT NULL)',
            name='check_product_or_service'
        ),
    )

    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    
    # Product fields (mutually exclusive with service)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=True)
    variant_id = Column(Integer, ForeignKey('variants.variant_id'), nullable=True)
    
    # Service field (mutually exclusive with product)
    service_id = Column(Integer, ForeignKey('services.service_id'), nullable=True)
    
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=False)  # Price at time of purchase
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("Variant", back_populates="order_items")
    service = relationship("Service", back_populates="order_items")


class OrderPayment(Base):
    __tablename__ = 'order_payments'

    payment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.now, nullable=False) # e.g., 'cash', 'card', 'online'
    status = Column(String, default='completed', nullable=False)  # e.g., 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    order = relationship("Order", back_populates="payments")


class SalesRecord(Base):
    __tablename__ = 'sales_records'

    record_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now, nullable=False)
    total_sales = Column(Float, nullable=False)  
    closing_cash = Column(Float, nullable=False) #default=500.00
    opening_cash = Column(Float, nullable=False) #default=500.00
    trasaction_count = Column(Integer, nullable=False, default=0)  # Number of transactions for the day
    remit_amount = Column(Float, nullable=False, default=0.0)  # Amount to remit 
    remarks = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False)

    cashout_transaction_id = Column(Integer, ForeignKey('daily_cashout_transactions.cashout_id'), nullable=True)


class CashoutTransaction(Base):
    __tablename__ = 'daily_cashout_transactions'

    cashout_id = Column(Integer, primary_key=True, index=True)
    cashout_date = Column(DateTime, default=datetime.now, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=False)

    # No relationship needed as this is a standalone transaction