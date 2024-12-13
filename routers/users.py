from fastapi import APIRouter, Depends,status
from sqlalchemy.orm import Session
from db.models import get_db
from schemas.users_schema import UserCreateModel
from db.models import User

router= APIRouter(
    prefix="/api/auth"
)



@router.post("/register")
async def create_user(data: UserCreateModel,db: Session = Depends(get_db)):
    print(data.id)
    if db.query(User).filter(username=data.username):
        print('exist krta h')
        return {"detail": "Not possible saar"}
