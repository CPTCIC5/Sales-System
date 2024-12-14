from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db.models import get_db, User
from schemas.users_schema import UserCreateModel, UserUpdateModel, LoginModel
from utils.auth import get_current_user, create_session, end_session

router= APIRouter(
    prefix="/api/auth"
)



@router.post("/register")
async def create_user(data: UserCreateModel, db: Session = Depends(get_db)):
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    elif db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    elif db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    elif len(data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    # Your success logic here
    new_user= User(
        username= data.username,
        email= data.email,
        phone_number= data.phone_no
    )
    new_user.set_password(data.password)
    print(new_user)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse({'detail': 'New User created'}, status_code=status.HTTP_201_CREATED)



@router.get('/user')
async def get_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    my_user= db.query(User).filter(User.id == current_user.id).first()
    return (my_user)

@router.delete('/delete-user')
async def edit_user(current_user: User = Depends(get_current_user), db: Session= Depends(get_db)):
    my_user= db.query(User).filter(User.id == current_user.id).first()
    if not my_user:
        return HTTPException(detail="wefuhweewf",status_code=status.HTTP_404_NOT_FOUND)
    db.delete(my_user)
    db.commit()
    return JSONResponse({'detail': "hmm deleted"}, status_code=status.HTTP_204_NO_CONTENT)

@router.patch('/edit-user/')
async def update_user(data: UserUpdateModel, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # First check if user exists
    my_user = db.query(User).filter(User.id == current_user.id).first()
    if not my_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check email uniqueness if it's being updated
    if data.email != my_user.email:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

    # Update user attributes
    my_user.email = data.email
    my_user.phone_number = data.phone_no
    

    try:
        db.commit()
        db.refresh(my_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse({'detail': 'User updated successfully'}, status_code=status.HTTP_200_OK)

@router.post("/login")
async def login(request: Request, data: LoginModel, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    
    if not user or not user.verify_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create session
    create_session(request, user)
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "message": "Login successful"
    }

@router.post("/logout")
async def logout(request: Request):
    end_session(request)
    return {"message": "Logged out successfully"}