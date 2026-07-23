from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, time
from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

login_attempts = {}
def check_rate_limit(username):
    current_time = datetime.now()
    if username not in login_attempts:
        login_attempts[username] = []
        return False
    
    login_attempts[username] = [
        t for t in login_attempts[username] if current_time - t < 900
    ]
    return len(login_attempts[username]) >= 5

SERET_KEY = "..."
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes= ["bcrypt"],
    deprecated= "auto"
)

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

OAuth2_scheme = OAuth2PasswordBearer(
    tokenUrl= "login"
)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(
        plain_password, 
        hashed_password
    )

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

def get_current_user(
        token: str = Depends(OAuth2_scheme),
        db: Session = Depends(get_db)):
    print("Inside get_current_user")
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code= 401,
                detail= "Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    return user