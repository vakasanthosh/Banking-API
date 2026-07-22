from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import RegisterRequest, LoginRequest
from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code = 400,
            detail = "username already exists"
        )

    existing_mobile = db.query(User).filter(
        User.mobile == user.mobile
    ).first()
    if existing_mobile:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )
    
    hashed_password = hash_password(user.password)

    new_user = User(
        username = user.username,
        mobile = user.mobile,
        password_hash = hashed_password,
        balance = 0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration Successful"
    }

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm =Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not db_user or not verify_password(
        form_data.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code= 401,
            detail = "Invalid credentials"
        )
    access_token = create_access_token(
        data= {"sub": db_user.username}
    )

    return{
        "access_token": access_token,
        "token_type": "bearer"
    }