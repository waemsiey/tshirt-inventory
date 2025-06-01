#API entry point all the routes are defined here
from typing import List
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas, crud.product_crud as pcrud
import crud.order_crud as ocrud
from service.order_service import place_order
from schemas import Product


app = FastAPI()

models.Base.metadata.create_all(bind=engine) # Create the database tables

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#route for the root path
@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}

#route to save an item
@app.post("/products")
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
   return pcrud.create_product(db=db, product=product)

#route to get all items
@app.get("/products" , response_model=List[Product])
def get_products(db: Session = Depends(get_db)):
    return pcrud.get_products(db=db)
    

#route to update an item
@app.put("/products/{product_id}")
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return pcrud.update_product(db=db, product_id=product_id, product=product)

#route to delete an item
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    return pcrud.delete_product(db=db, product_id=product_id)

@app.post("/orders")
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return place_order(db, order)

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return ocrud.get_orders(db=db)