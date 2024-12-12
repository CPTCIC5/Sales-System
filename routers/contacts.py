from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.models import get_db

router = APIRouter(
    prefix="/api/contacts"
)

@router.get('/add')
async def add_contact(db: Session = Depends(get_db)):
    return {"E"}