from pydantic import BaseModel, field_validator
from datetime import datetime

class RegisterRequest(BaseModel):
    username: str
    mobile: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if value.strip() == "":
            raise ValueError("username cannot be empty")
        return value
    
    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value):
        if not value.isdigit(): 
            raise ValueError("Mobile number must contain only digits")
        if len(value) != 10:
            raise ValueError("Mobile number must contain exactly 10 digits")

        if value[0] not in "6789":
            raise ValueError("Mobile number must start with 6, 7, 8 or 9")
        return value
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must contain at least 8 characters")
        return value
    
class DepositRequest(BaseModel):
    card_holder_name: str
    card_number: str
    cvv: str
    expiry_date: str
    amount: float

class WithdrawRequest(BaseModel):
    amount: float

class TransferRequest(BaseModel):
    receiver_mobile: str
    amount: float 

class LoginRequest(BaseModel):
    username: str
    password: str

class TransactionResponse(BaseModel):
    type: str
    amount: float
    counterparty_username: str | None
    created_at: datetime

    class Config:
        from_attributes = True