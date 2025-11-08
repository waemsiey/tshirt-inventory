from fastapi import FastAPI, Depends, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from typing import List, Optional
import json
from fastapi.responses import JSONResponse

# Local imports
from database import SessionLocal, engine
import models, schemas
import crud.product_crud as pcrud
import crud.service_crud as scrud
import crud.order_crud as ocrud
from storage import upload_image_to_supabase
from models import Product, Variant, Service

# Initialize FastAPI
app = FastAPI(title="Inventory-API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------
# Product Routes
# --------------------------
@app.post("/products", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return pcrud.create_product(db=db, product=product)

@app.get("/products", response_model=List[schemas.Product])
def get_products(db: Session = Depends(get_db)):
    return pcrud.get_products(db=db)

@app.get("/search-product", response_model=List[schemas.Product])
def search_products(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return pcrud.search_products(db=db, search=search)

@app.get("/products/count")
def get_sold_count(db: Session = Depends(get_db)):
    return {"count": ocrud.count_orders(db)}

@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int, 
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db)
):
    return pcrud.update_product(db=db, product_id=product_id, product=product)

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    return pcrud.delete_product(db=db, product_id=product_id)

# --------------------------
# Service Routes
# --------------------------
@app.post("/services", response_model=schemas.Service)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    return scrud.create_service(db=db, service=service)

@app.get("/services", response_model=List[schemas.Service])
def get_services(db: Session = Depends(get_db)):
    return scrud.get_services(db=db)

# --------------------------
# Order Routes
# --------------------------
@app.post("/orders", response_model=schemas.OrderDB)
async def create_production_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db)
):
    try:
        # Process order
        result = ocrud.create_order(db, order.dict())
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/orders", response_model=List[schemas.OrderDB])
def get_orders(db: Session = Depends(get_db)):
    return ocrud.get_orders(db=db)

@app.get("/sold/count")
def get_product_count(db: Session = Depends(get_db)):
    return {"count": ocrud.count_orders(db)}


#---------------------------
# Order Payment Routes
#---------------------------
@app.get("/order-payments", response_model=List[schemas.OrderPaymentResponse])
def get_order_payments(db: Session = Depends(get_db)):
    """Get all order payments"""
    return ocrud.get_order_payments(db=db)

@app.post("/order-payments", response_model=schemas.OrderPaymentResponse)
def create_order_payment(payment: schemas.OrderPaymentCreate,db: Session = Depends(get_db)):
    """Create a new order payment"""
    return ocrud.create_order_payment(db=db, payment=payment)


#--------------------------
# Payment Sum
#--------------------------
@app.get("/total-payments", response_model=schemas.TotalPaymentsResponse)
def get_total_payments(db: Session = Depends(get_db)):
    """Get total payments made"""
    total = ocrud.get_total_payments_made(db=db)
    return {"total_payments": total}

@app.get("/service-payments", response_model=List[schemas.ServicePaymentResponse])
def get_service_payments(db: Session = Depends(get_db)):
    """Get total payments per service"""
    services = db.query(models.Service).all()
    results = []

    for service in services:
        total = ocrud.get_total_payments_for_item(db=db, item_id=service.service_id, item_type='service')
        results.append({
            "id": service.service_id,
            "name": service.name,
            "total_payments": total
        })

    return results

# --------------------------
# Utility Routes
# --------------------------
@app.post("/upload-image")
async def upload_image(image: UploadFile = File(...)):
    content = await image.read()
    url = await upload_image_to_supabase(
        file_name=image.filename,
        file_content=content,
        content_type=image.content_type
    )
    return {"image_url": url}

@app.get("/user-info")
async def log_info(request: Request):
    client_info = {
        "ip": request.headers.get("X-Forwarded-For") or request.client.host,
        "user_agent": request.headers.get("User-Agent"),
        "language": request.headers.get("Accept-Language")
    }
    print(f"Client info: {client_info}")
    return client_info


@app.get("/")
def read_root():
    return {"message": "Welcome to the E-Commerce API"}

@app.post("/debug-order")
async def debug_order(
    request: Request,  # Changed from 'order' to raw request
    db: Session = Depends(get_db)
):
    """Endpoint to catch ALL validation errors"""
    try:
        raw_data = await request.json()
        print("\n🔥 RAW REQUEST DATA:")
        print(raw_data)

        # Manually validate basic structure
        if "items" not in raw_data:
            return JSONResponse(
                status_code=422,
                content={"detail": "Missing 'items' array"}
            )

        # Print database state
        print("\n📦 DATABASE STATE:")
        print("Products:", [p[0] for p in db.query(Product.product_id).all()])
        print("Variants:", [(v[0], v[1]) for v in db.query(Variant.variant_id, Variant.product_id).all()])
        print("Services:", [s[0] for s in db.query(Service.service_id).all()])

        # Try parsing with your schema
        try:
            order = schemas.OrderCreate(**raw_data)
            return {
                "status": "VALID",
                "order": order.dict(),
                "calculated_total": sum(
                    item.price * item.quantity 
                    for item in order.items
                ) - order.discount
            }
        except Exception as e:
            print("\n❌ SCHEMA VALIDATION ERROR:")
            print(str(e))
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "Schema validation failed",
                    "error": str(e),
                    "received_data": raw_data
                }
            )

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=422,
            content={"detail": "Invalid JSON format"}
        )
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

