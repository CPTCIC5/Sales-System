from pydantic import BaseModel,EmailStr, model_validator, Field
from openai import OpenAI
import random
client= OpenAI()

def create_assistant_organization(name, business_model):
    base_context= ""
    if business_model == "B2B":
        base_context= base_context + f"""
        
        Your Role:
        - Act as a professional B2B sales representative
        - Focus on business needs and pain points
        [... rest of B2B specific instructions ...]
        """
    
    elif business_model == "B2C":
        base_context= base_context + """
        Your Role:
        - Act as a friendly customer service representative
        - Focus on individual needs and preferences
        - Keep language simple and jargon-free
        - Emphasize personal benefits
        
        Key Objectives:
        1. Understand personal needs
        2. Identify individual preferences
        3. Build personal connection
        4. Guide towards appropriate solution
        
        Qualification Process:
        1. Understand Requirements:
           - Ask about specific needs
           - Explore usage scenarios
        
        2. Confirm Decision Making:
           - Understand timeline
           - Discuss budget expectations
        
        Meeting Link Sharing Criteria:
        - Share meeting link when:
            1. Customer shows clear interest
            2. Has specific needs that require detailed discussion
            3. Requests more information
        """
    
    else:  # "BOTH"
        base_context= """
        Your Role:
        - Adapt your approach based on the conversation
        - Start neutral and determine if speaking with business or individual
        - Adjust language and focus accordingly
        
        Initial Assessment:
        - Ask open-ended questions about their interest
        - Listen for business or personal use indicators
        - Adapt qualification process based on response
        
        Key Objectives:
        1. Identify if business or personal use
        2. Adjust communication style accordingly
        3. Follow appropriate qualification process
        """
    assistant= client.beta.assistants.create(
        name=name,
        model="gpt-4o",
        instructions=base_context,
        tools=[{"type": "file_search"}],
    )
    return assistant.id

def create_vspace_organization(name):
    vector_store = client.beta.vector_stores.create(
    name=name,
    )
    return (vector_store.id)


class OrganizationCreateModel(BaseModel):
    root_user_id: int= None
    business_name: str
    business_webURL: str
    industry_type: str
    assistant_id: str= None
    vspace_id:str=None
    business_model: str = Field(..., pattern="^(B2B|B2C|BOTH)$")

    @model_validator(mode="before")
    @classmethod
    def populate_assistant_id(cls, values):
        if "business_name" in values:
            values["assistant_id"] = create_assistant_organization(values["business_name"], values["business_model"])
        return values
    
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
    api_key: str= None

class OrganizationFiles(BaseModel):
    filesystem_id: int
    file_name: str
    file_path: str