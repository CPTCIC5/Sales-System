from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.models import get_db

router= APIRouter(
    prefix="/api/organizations"
)

@router.get('/create')
async def add_org(db: Session = Depends(get_db)):
    return {"F"}