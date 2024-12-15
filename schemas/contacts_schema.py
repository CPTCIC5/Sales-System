from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ContactModel(BaseModel):
    org_id: int
    name: str
    phone_number: Optional[str] = None
    industry: Optional[str] = None
    website_url: Optional[str] = None
    avatar: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    is_favorite: bool = False

class ContactUpdateModel(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    industry: Optional[str] = None
    website_url: Optional[str] = None
    avatar: Optional[str] = None
    is_favorite: Optional[bool] = None

class TagModel(BaseModel):
    tag_name: str
    color_code: Optional[str] = None

class TagUpdateModel(BaseModel):
    tag_name: Optional[str] = None
    color_code: Optional[str] = None

class GroupModel(BaseModel):
    name: str

class GroupUpdateModel(BaseModel):
    name: str

class PromptModel(BaseModel):
    input_text: str
    response_text: Optional[str] = None
    response_image: Optional[str] = None