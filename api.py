from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db.models import Base, User, Profile, Organization, OrganizationKeys, Category, Product, OrganizationFileSystem
from db.models import OrganizationInvite, Contact, Tag, Group, Prompt
from pydantic import BaseModel
from datetime import datetime

# Create FastAPI app
app = FastAPI()

# Database configuration
DATABASE_URL = "sqlite:///test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    joined_at: datetime
    is_active: bool
    class Config:
        from_attributes = True

# API endpoints
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        username=user.username,
        password=user.password,  # Note: Should hash password in production
        email=user.email,   
        phone_number=user.phone_number
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_user

@app.get("/users/", response_model=list[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Organization endpoints
class OrganizationCreate(BaseModel):
    root_user_id: int
    business_name: str
    business_webURL: str
    industry_type: str = None
    vspace_id: str

class OrganizationResponse(BaseModel):
    id: int
    business_name: str
    business_webURL: str
    industry_type: str= None
    created_at: datetime
    class Config:
        from_attributes = True

@app.post("/organizations/", response_model=OrganizationResponse)
async def create_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    db_org = Organization(**org.model_dump())
    db.add(db_org)
    try:
        db.commit()
        db.refresh(db_org)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_org

@app.get("/organizations/", response_model=list[OrganizationResponse])
async def get_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    organizations = db.query(Organization).offset(skip).limit(limit).all()
    return organizations

# Product endpoints
class ProductCreate(BaseModel):
    org_id: int
    title: str
    description: str = None
    image: str = None
    product_type_id: int = None
    category_id: int = None
    price_per_quantity: float = None
    status: str = None

class ProductResponse(BaseModel):
    id: int
    title: str
    description: str= None
    price_per_quantity: float= None
    created_at: datetime
    class Config:
        from_attributes = True

@app.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    try:
        db.commit()
        db.refresh(db_product)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_product

@app.get("/products/", response_model=list[ProductResponse])
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

# Contact endpoints
class ContactCreate(BaseModel):
    org_id: int
    name: str
    phone_number: str = None
    industry: str = None
    website_url: str = None
    utm_campaign: str = None
    utm_source: str = None
    utm_medium: str = None

class ContactResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    industry: str
    created_at: datetime
    class Config:
        from_attributes = True

@app.post("/contacts/", response_model=ContactResponse)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    try:
        db.commit()
        db.refresh(db_contact)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_contact

@app.get("/contacts/", response_model=list[ContactResponse])
async def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return contacts

if __name__ == "__main__":
    import uvicorn
    # Create tables
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, port=8000)