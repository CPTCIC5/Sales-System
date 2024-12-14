from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.models import get_db,User
from utils.auth import get_current_user
router= APIRouter(
    prefix="/api/organizations"
)

@router.get('/create')
async def create_org(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass