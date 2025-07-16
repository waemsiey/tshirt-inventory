#Database logic 
from sqlalchemy.orm import Session , joinedload
from models import Product , Variant
from schemas import ProductCreate
from datetime import datetime
from typing import Optional
from sqlalchemy import or_

#Create
def create_product(db: Session, product: ProductCreate):
    db_product = Product(
        name=product.name,
        color=product.color,
        image_url=product.image_url, 
        created_at=datetime.now()
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    for variant in product.variants:
        db_variant = Variant(
            product_id=db_product.product_id,
            size=variant.size,
            quantity=variant.quantity,
            selling_price=variant.selling_price,
            item_cost=variant.item_cost,
            updated_at=datetime.now()
        )
        db.add(db_variant)

    db.commit()
    return db_product

#Read
def get_products(db: Session):
    return db.query(Product).options(joinedload(Product.variants)).all()

#returns product by color seach or name search
def search_products(db: Session, search: Optional[str] = None):
    query = (
        db.query(Product)
        .join(Variant)
        .options(joinedload(Product.variants))
        .filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.color.ilike(f"%{search}%")
            )
        )
        .distinct()
    ) if search else db.query(Product).options(joinedload(Product.variants))

    products = query.all()

    if search:
        search_lower = search.lower()
        for product in products:
            product.variants = [
                v for v in product.variants
                if search_lower in (v.color or '').lower() or search_lower in (product.name or '').lower()
            ]

    # Filter out products with no matching variants (optional)
    products = [p for p in products if p.variants]

    return products

#Count products
def count_products(db: Session):
    return db.query(Variant).count()

#Update
def update_product(db: Session, product_id: int, product: ProductCreate):
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        return None
    db_product.name = product.name
    db_product.description = product.description

    db.commit()
    db.refresh(db_product)
    return db_product   

#Delete
def delete_product(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        return None

    db.delete(db_product)
    db.commit()
    return db_product

#Add Variant to each product 
def create_variant(db: Session, product_id: int, variant):
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        return None

    db_variant = Variant(
        size=variant.size,
        quantity=variant.quantity,
        selling_price=variant.selling_price,
        item_cost=variant.item_cost,
        updated_at=datetime.now(),
        image_url=variant.image_url,
    )

    db.commit()
    db.refresh(db_variant)
    return db_variant

#Updating Variant
def update_variant(db: Session, variant_id: int, variant):
    db_variant = db.query(Product.variants).filter(Product.variants.variant_id == variant_id).first()
    if not db_variant:
        return None

    db_variant.size = variant.size
    db_variant.quantity = variant.quantity
    db_variant.selling_price = variant.selling_price
    db_variant.item_cost = variant.item_cost
    db_variant.updated_at = datetime.now()

    db.commit()
    db.refresh(db_variant)
    return db_variant

#Delete Variant
def delete_variant(db: Session, variant_id: int):
    db_variant = db.query(Product.variants).filter(Product.variants.variant_id == variant_id).first()
    if not db_variant:
        return None

    db.delete(db_variant)
    db.commit()
    return db_variant

#Get all variants of a product
def get_variants_by_product(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        return None
    return db_product.variants

