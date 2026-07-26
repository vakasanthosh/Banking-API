from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, time
from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

# Dictionary used to store login attempts
login_attempts = {}

# Rate Limiting Function
# Prevents brute-force login attacks by limiting failed login attempts.
def check_rate_limit(username):
    current_time = datetime.now()
    # If the username is new, create an empty list
    if username not in login_attempts:
        login_attempts[username] = []
        return False
    
    # Remove attempts older than 15 minutes
    login_attempts[username] = [
        t for t in login_attempts[username] if current_time - t < 900
    ]
    return len(login_attempts[username]) >= 5

# JWT Configuration
SCERET_KEY = "..."
ALGORITHM = "HS256"

# Password hashing configuration
pwd_context = CryptContext(
    schemes= ["bcrypt"],
    deprecated= "auto"
)

# Secret key used for JWT token generation
# Encryption algorithm
# Token validity time (30 minutes)
SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 configuration
OAuth2_scheme = OAuth2PasswordBearer(
    tokenUrl= "login"
)

# Password Hashing
def hash_password(password: str):
    return pwd_context.hash(password)

# Password Verification
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(
        plain_password, 
        hashed_password
    )

# Create JWT Token
def create_access_token(data: dict):
    # Copy user data
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # Add expiry to payload
    to_encode.update({"exp": expire})
    # Encode payload into JWT token
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

# Get Current Logged-in User
def get_current_user(
        token: str = Depends(OAuth2_scheme),
        db: Session = Depends(get_db)):
    print("Inside get_current_user")
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        # Extract username from token
        username = payload.get("sub")

        # If username is missing
        if username is None:
            raise HTTPException(
                status_code= 401,
                detail= "Invalid token"
            )
    except JWTError:
        # Token is invalid or expired
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
    # Return logged-in user
    return user