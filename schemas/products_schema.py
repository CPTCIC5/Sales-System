from pydantic import BaseModel
from typing import Optional

class ProductModel(BaseModel):
    title: str
    desc: str= None
    image: Optional[str] = None
    category_id: int
    price_per_quantity: float
    currency: str
    is_available: bool = True

class CategoryModel(BaseModel):
    name: str