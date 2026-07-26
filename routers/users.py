import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import RegisterRequest, LoginRequest
from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, create_access_token, check_rate_limit, login_attempts

#create router
router = APIRouter()

#register end point
#register a new user
@router.post("/register")
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db)):
    
    #check if user is already exists
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code = 400,
            detail = "username already exists"
        )
    #checks mobile number is already exists
    existing_mobile = db.query(User).filter(
        User.mobile == user.mobile
    ).first()
    if existing_mobile:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )
    
    #encrypt password befor storing
    hashed_password = hash_password(user.password)

    #create new user object
    new_user = User(
        username = user.username,
        mobile = user.mobile,
        password_hash = hashed_password,
        balance = 0
    )
    #save user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration Successful"
    }

#login endpoint-- authenticates the user and returns a jwt token
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm =Depends(),
    db: Session = Depends(get_db)
):
    #search user by username
    db_user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    #check login rate limit
    if check_rate_limit(form_data.username):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later."
        )

    #verify username and password
    if not db_user or not verify_password(
        form_data.password,
        db_user.password_hash
    ):
        #record failed login attempts
        login_attempts.setdefault(form_data.username, []).append(time.time())

        raise HTTPException(
            status_code= 401,
            detail = "Invalid credentials"
        )
    #clear failed attempts after successful login
    login_attempts.pop(form_data.username, None)  

    #generate jwt access token
    access_token = create_access_token(
        data= {"sub": db_user.username}
    )
    #return token to client
    return{
        "access_token": access_token,
        "token_type": "bearer"
    }