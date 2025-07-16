from typing import List, Optional
from unittest import result
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from fastapi import HTTPException
import models
from models import OrderItem, Order, OrderPayment, SalesRecord, CashoutTransaction
from schemas import OrderResponse, OrderPaymentCreate, SalesRecordCreate, CashoutTransactionCreate

def create_order(db: Session, order_data: dict):
    try:
        # Create order
        db_order = models.Order(
            order_date=datetime.now(),
            total_price=order_data['total_price']
        )
        db.add(db_order)
        db.flush()  # Get order_id
        
        # Process items
        items = []
        for item in order_data['items']:
            # Validate product/variant
            if item.get('product_id'):
                product = db.query(models.Product).get(item['product_id'])
                if not product:
                    raise ValueError(f"Product {item['product_id']} not found")
                
                if item.get('variant_id'):
                    variant = db.query(models.Variant).filter_by(
                        variant_id=item['variant_id'],
                        product_id=item['product_id']
                    ).first()
                    if not variant:
                        raise ValueError(f"Variant {item['variant_id']} not found")
                    if variant.quantity < item['quantity']:
                        raise ValueError("Not enough stock")
                    variant.quantity -= item['quantity']
            
            # Validate service
            elif item.get('service_id'):
                service = db.query(models.Service).get(item['service_id'])
                if not service:
                    raise ValueError(f"Service {item['service_id']} not found")
            
            # Create item
            db_item = models.OrderItem(
                order_id=db_order.order_id,
                **{k: v for k, v in item.items() if v is not None}
            )
            db.add(db_item)
            items.append(db_item)
        
        db.commit()
        
        # Return properly structured data
        return {
            "order_id": db_order.order_id,
            "order_date": db_order.order_date,
            "total_price": db_order.total_price,
            "items": [{
                "order_item_id": i.order_item_id,
                "order_id": i.order_id,
                "product_id": i.product_id,
                "service_id": i.service_id,
                "variant_id": i.variant_id,
                "quantity": i.quantity,
                "price": i.price
            } for i in items]
        }

    except Exception as e:
        db.rollback()
        raise
def get_orders(db: Session):
    orders = (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.payments)
        )
        .all()
    )

    result = []
    for order in orders:
        order_data = {
            "order_id": order.order_id,
            "order_date": order.order_date,
            "total_price": float(order.total_price),
            "payment_status": order.payment_status,
            "items": [],
            "payments": []
        }

        for item in order.items:
            item_data = {
                "order_item_id": item.order_item_id,
                "order_id": item.order_id,
                "product_id": item.product_id,
                "service_id": item.service_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "price": float(item.price)
            }
            order_data["items"].append(item_data)

        for payment in order.payments:
            payment_data = {
                "payment_id": payment.payment_id,
                "order_id": payment.order_id,
                "amount": payment.amount,
                "payment_date": payment.payment_date,
                "status": payment.status,
                "created_at": payment.created_at,
                "updated_at": payment.updated_at,
            }
            order_data["payments"].append(payment_data)

        result.append(OrderResponse.parse_obj(order_data))

    return result  

#Count products
def count_orders(db: Session):
    return db.query(OrderItem).count()



# -----------------------
# OrderPayment CRUD
# -----------------------

def create_order_payment(db: Session, payment: OrderPaymentCreate) -> OrderPayment:
    """
    Creates a payment for an order and automatically updates order status.
    Status rules:
    - 'pending' (default when order is created)
    - 'partial' (when payment < total)
    - 'complete' (when payment >= total)
    """
    # 1. Check if order exists
    order = db.query(Order).get(payment.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 2. Calculate current payment totals
    existing_payments = db.query(OrderPayment).filter(
        OrderPayment.order_id == payment.order_id
    ).all()
    
    paid_amount = sum(p.amount for p in existing_payments)
    new_total_paid = paid_amount + payment.amount

    # 3. Validate payment doesn't exceed order total
    if new_total_paid > order.total_price:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Payment would exceed order total. "
                f"Order total: {order.total_price}, "
                f"Already paid: {paid_amount}, "
                f"Remaining: {order.total_price - paid_amount}"
            )
        )

    # 4. Create the payment record
    db_payment = OrderPayment(
        order_id=payment.order_id,
        amount=payment.amount,
        payment_date=payment.payment_date or datetime.now(),
        status="completed"  # Individual payment status
    )
    db.add(db_payment)
    db.flush()  # Get the payment ID if needed

    # 5. Update order status (critical section)
    if new_total_paid >= order.total_price:
        order.status = "complete"
        order.payment_status = "complete"
    elif new_total_paid > 0:
        order.status = "processing"  # Or keep as 'pending' if you prefer
        order.payment_status = "partial"
    else:
        order.status = "pending"
        order.payment_status = "pending"

    # 6. If you have direct payment_id reference in Order
    if hasattr(Order, 'payment_id'):
        order.payment_id = db_payment.payment_id

    db.commit()
    db.refresh(db_payment)
    return db_payment

# Small helper function (could add to your CRUD file)
def update_order_payment_status(db: Session, order_id: int):
    order = db.query(Order).get(order_id)
    if not order:
        return
    
    total_paid = sum(p.amount for p in order.payments)
    
    if total_paid >= order.total_price:
        order.payment_status = "paid"
    elif total_paid > 0:
        order.payment_status = "partial"
    else:
        order.payment_status = "pending"
    
    db.commit()


def get_order_payments(db: Session, skip: int = 0, limit: int = 100) -> List[OrderPayment]:
    return db.query(OrderPayment).offset(skip).limit(limit).all()


# -----------------------
# SalesRecord CRUD
# -----------------------

def create_sales_record(db: Session, record: SalesRecordCreate) -> SalesRecord:
    db_record = SalesRecord(
        date=record.date or datetime.now(),
        total_sales=record.total_sales,
        opening_cash=record.opening_cash,
        closing_cash=record.closing_cash,
        trasaction_count=record.trasaction_count,
        remit_amount=record.remit_amount,
        remarks=record.remarks,
        cashout_transaction_id=record.cashout_transaction_id,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_sales_records(db: Session, skip: int = 0, limit: int = 100) -> List[SalesRecord]:
    return db.query(SalesRecord).order_by(SalesRecord.date.desc()).offset(skip).limit(limit).all()


def get_sales_record_by_date(db: Session, target_date: datetime) -> Optional[SalesRecord]:
    return db.query(SalesRecord).filter(SalesRecord.date == target_date).first()


# -----------------------
# CashoutTransaction CRUD
# -----------------------

def create_cashout_transaction(db: Session, cashout: CashoutTransactionCreate) -> CashoutTransaction:
    db_cashout = CashoutTransaction(
        cashout_date=cashout.cashout_date or datetime.now(),
        amount=cashout.amount,
        reason=cashout.reason
    )
    db.add(db_cashout)
    db.commit()
    db.refresh(db_cashout)
    return db_cashout


def get_cashout_transactions(db: Session, skip: int = 0, limit: int = 100) -> List[CashoutTransaction]:
    return db.query(CashoutTransaction).order_by(CashoutTransaction.cashout_date.desc()).offset(skip).limit(limit).all()

def get_total_payments_made(db: Session) -> float:
    total = db.query(OrderPayment).with_entities(func.sum(OrderPayment.amount)).scalar()
    return total if total else 0.0

#For getting total payments made for a service or product
def get_total_payments_for_item(db: Session, item_id: int, item_type: str) -> float:
    if item_type == 'product':
        payments = db.query(OrderPayment).join(OrderItem).filter(OrderItem.product_id == item_id).all()
    elif item_type == 'service':
        payments = db.query(OrderPayment).join(OrderItem).filter(OrderItem.service_id == item_id).all()
    else:
        raise ValueError("Invalid item type. Use 'product' or 'service'.")

    total = sum(payment.amount for payment in payments)
    return total if total else 0.0

