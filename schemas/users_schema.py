from pydantic import BaseModel,EmailStr,Field


class UserCreateModel(BaseModel):
    id: int
    username: str
    password: str
    confirm_password: str= Field(exclude=True)
    email: EmailStr
    phone_no: str
    is_active: bool= True
    groups: list[str]= None
    tags: list[str]= None