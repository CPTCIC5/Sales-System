from pydantic import BaseModel,EmailStr, model_validator, Field
from openai import OpenAI
import random
client= OpenAI()

def create_vspace_organization(name):
    vector_store = client.beta.vector_stores.create(
    name=name
    )
    return (vector_store.id)


class OrganizationCreateModel(BaseModel):
    root_user_id: int
    business_name: str
    business_webURL: str
    industry_type: str
    vspace_id: str= None

    @model_validator(mode="before")
    @classmethod
    def populate_vspace_id(cls, values):
        if "business_name" in values:
            values["vspace_id"] = create_vspace_organization(values["business_name"])
        return values
    

class OrganizationInviteCreateModel(BaseModel):
    accepted: bool= False
    invite_code: str = Field(default_factory=lambda: random.randint(100000, 999999))
    email: EmailStr



class OrganizationKeysModel(BaseModel):
    organization_id: int
    whatsapp_business_token: str = None


class OrganizationFileSystemUpdate(BaseModel):
    api: str= None

class OrganizationFiles(BaseModel):
    filesystem_id: int
    file_name: str
    file_path: str