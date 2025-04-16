from models import Product 
from database import MockDatabase 
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional

app = FastAPI()
# Update the path to point to the CSV file
db = MockDatabase("data/merged_10K_updated.csv")
db.load_data()
print("Loading data from:", db.total_records)

@app.get("/")
def read_root():
    return {"message": "Welcome to the e-commerce API!"}

@app.get("/products")
def get_products(skip: int = 0, limit: int = 100):
    products = db.get_products()
    return products[skip:skip+limit]

@app.get("/products/{product_id}")
def get_product(product_id: str):
    products = db.get_products()
    product = next((p for p in products if str(p["id"]) == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/search")
def search_products(query: str = Query(..., description="Search term for product name or description")):
    return db.search_products(query)

@app.get("/count")
def get_product_count():
    return {"total": db.get_product_count()}
