from fastapi import APIRouter, HTTPException, Query
from database import QdrantDB

router = APIRouter()
db = QdrantDB()

@router.get("/")
def read_root():
    return {"message": "Welcome to the e-commerce API!"}

@router.get("/products")
def get_products(skip: int = 0, limit: int = 100):
    products = db.get_products()
    return products[skip:skip+limit]

@router.get("/products/{product_id}")
def get_product(product_id: str):
    products = db.get_products()
    product = next((p for p in products if str(p.get("id")) == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/search")
def search_products(query: str = Query(..., description="Search term for product name or description")):
    return db.search_products(query)

@router.get("/count")
def get_product_count():
    return db.get_product_count()
