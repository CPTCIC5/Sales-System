from pydantic import BaseModel,model_validator
from datetime import datetime
from typing import Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from fastapi import Depends
from db.models import get_db
from db.models import Organization
from dotenv import load_dotenv

load_dotenv()
client= OpenAI()

class ContactModel(BaseModel):
    org_id: int
    name: str
    phone_number: str
    industry: Optional[str] = None
    website_url: Optional[str] = None
    avatar: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    is_favorite: bool = False
    thread_id: str = None

    @model_validator(mode='before')
    def populate_thread_id(cls, values):
        if not values.get('thread_id'):
            thread = client.beta.threads.create()
            values['thread_id'] = thread.id
        return values

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



class GroupModel(BaseModel):
    name: str

class GroupUpdateModel(BaseModel):
    name: str

class PromptModel(BaseModel):
    input_text: str
    response_text: Optional[str] = None
    response_image: Optional[str] = None