from pydantic import BaseModel

class Product(BaseModel):
    id: int
    product_name: str
    description: str
    category: str
    price: float
