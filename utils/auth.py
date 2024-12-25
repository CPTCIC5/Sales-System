from fastapi import Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from db.models import User, get_db
from typing import Optional

# Configuration
SECRET_KEY = "your-secret-key-keep-it-secret"  # Use environment variable in production

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def create_session(request: Request, user: User):
    request.session["user_id"] = user.id
    request.session["username"] = user.username

def end_session(request: Request):
    request.session.clear()

from sqlalchemy.orm import Session
from db.models import get_db, Product,OrganizationFileSystem
from fastapi import APIRouter,Depends
import requests

router= APIRouter(
    prefix="/api/helper"
)

@router.get("/products/org/{org_id}")
def get_organization_products(org_id: int, db: Session = Depends(get_db)):
    org_products= db.query(Product).filter(Product.org_id == org_id).all()
    my_org_keys= db.query(OrganizationFileSystem).filter(OrganizationFileSystem.org_id == org_id).first()
    print(my_org_keys.api)
    if my_org_keys.api:
        if my_org_keys.api and my_org_keys.api_key:
            headers= {"Authorization": f"Bearer {my_org_keys.api_key}"} 
            url= requests.get(my_org_keys.api, headers=headers)
        else:
            url= requests.get(my_org_keys.api)
        if url.status_code == 200:
            data= url.json()
        datt= []
        datt.append(org_products)
        datt.append(data)
    return datt