from pydantic import BaseModel
from typing import Optional

class ProductModel(BaseModel):
    title: str
    desc: str= None
    image: Optional[str] = None
    product_type: int
    category_id: int
    price_per_quantity: float
    is_available: bool = True

class CategoryModel(BaseModel):
    name: str