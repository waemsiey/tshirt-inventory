from schemas import OrderCreate
from sqlalchemy.orm import Session
from models import Orders
from datetime import datetime

#getting all orders
def get_orders(db: Session):
    return db.query(Orders).all()