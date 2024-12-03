from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import List

class User(BaseModel):
    id: int
    username: str
    password: str
    joined_at: datetime= datetime.now()


class Organization(BaseModel):
    id: int
    name: str
    root_user: User
    members: List

class Industry(str, Enum):
    ECOMMERCE= "ecommerce"
    SHOPIFY= "shopify" 
    HOSPITALITY= "hospitality"
    REAL_ESTATE= "real e-state"

class Lead(BaseModel):
    id: int
    org_id: int | None = None
    name: str
    business_name: str
    contact_number: str
    website_url: str
    industry: Industry
    thread_id: str | None = None
    created_at: datetime = datetime.now()