from sqlalchemy.orm import Session
from models import Product, Orders, Variants
from schemas import OrderCreate
from datetime import datetime
from fastapi import HTTPException

def place_order(db: Session, order: OrderCreate):
    variants = db.query(Variants).filter(
        Variants.product_id == order.product_id,
        Variants.size == order.size,
        Variants.color == order.color
        ).first()

    if not variants:
        raise HTTPException(status_code=404, detail="Product not found")

    if variants.quantity < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    #Updating the stocks of the variant 
    variants.quantity -= order.quantity
    variants.updated_at = datetime.now()

    #Getting the total amount of order
    order.total_price = variants.price * order.quantity

    db_order = Orders(
        product_id=order.product_id,
        quantity=order.quantity,
        size = order.size,
        color = order.color,
        order_date=datetime.now(),
        total_price=order.total_price
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return db_order
