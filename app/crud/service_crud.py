from sqlalchemy.orm import Session
from datetime import datetime
from models import Service
from schemas import ServiceCreate

def get_service(db: Session, service_id: int):
    return db.query(Service).filter(Service.service_id == service_id).first()

def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Service).offset(skip).limit(limit).all()

def create_service(db: Session, service: ServiceCreate):
    db_service = Service(
        name=service.name,
        size=service.size,
        print_price=service.print_price,
        image_url=service.image_url,
        created_at=datetime.now()
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

# def update_service(db: Session, service_id: int, service: ServiceUpdate):
#     db_service = db.query(Service).filter(Service.service_id == service_id).first()
#     if not db_service:
#         return None
    
#     update_data = service.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_service, key, value)
    
#     db.commit()
#     db.refresh(db_service)
#     return db_service

def delete_service(db: Session, service_id: int):
    db_service = db.query(Service).filter(Service.service_id == service_id).first()
    if not db_service:
        return False
    
    db.delete(db_service)
    db.commit()
    return True