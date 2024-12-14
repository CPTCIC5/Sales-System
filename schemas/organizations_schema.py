from pydantic import BaseModel,HttpUrl,Field
from openai import OpenAI

client= OpenAI()

def create_vspace_organization(name):
    vector_store = client.beta.vector_stores.create(
    name=name
    )
    return (vector_store.id)


class OrganizationCreateModel(BaseModel):
    root_user_id: int
    business_name: str
    business_webURL: HttpUrl
    industry_type: str
    vspace_id: str= Field(default_factory=create_vspace_organization(business_name))