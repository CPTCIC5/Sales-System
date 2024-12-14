from pydantic import BaseModel,EmailStr,Field
from datetime import datetime

class UserCreateModel(BaseModel):
    username: str
    password: str = Field(gt=7)
    confirm_password: str= Field(exclude=True)
    email: EmailStr
    phone_no: str


class UserUpdateModel(BaseModel):
    email: EmailStr
    phone_no: str


class LoginModel(BaseModel):
    username: str
    password: str