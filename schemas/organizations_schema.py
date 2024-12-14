from pydantic import BaseModel,Field, model_validator
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
    business_webURL: str
    industry_type: str
    vspace_id: str= None

    @model_validator(mode="before")
    @classmethod
    def populate_vspace_id(cls, values):
        if "business_name" in values:
            values["vspace_id"] = create_vspace_organization(values["business_name"])
        return values