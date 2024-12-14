from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.models import get_db, User
from utils.auth import get_current_user

router = APIRouter(
    prefix="/api/contacts"
)

@router.get('/add')
async def add_contact(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {
        "message": f"Adding contact for user: {current_user.username}"
    }