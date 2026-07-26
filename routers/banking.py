from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User, Transaction
from app.schemas import DepositRequest, WithdrawRequest, TransferRequest, TransactionResponse
from app.auth import get_current_user
from services.banking_service import get_balance_service, deposit_service, withdraw_service, transfer_service 

# Create router object
router = APIRouter()

# Deposit Endpoint
# Allows the logged-in user to deposit money.
@router.post("/deposit")
def deposit(
    deposit: DepositRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):  
    # Call deposit service
    return deposit_service(db, 
        current_user,
        deposit
    )

# Withdraw Endpoint
@router.post("/withdraw")
def withdraw(
    withdraw: WithdrawRequest,
    db: Session = Depends(get_db),
    current_user: User =Depends(get_current_user)
):
    return withdraw_service(
        db,
        current_user,
        withdraw
    )

# Transfer Endpoint
@router.post("/transfer")
def transfer(
    transfer: TransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return transfer_service(
        db = db,
        current_user= current_user,
        transfer = transfer
    )

# Balance Endpoint
# Returns the current user's account balance.
@router.get("/balance")
def get_balance(
    current_user: User = Depends(get_current_user)
):
    return get_balance_service(current_user)

# Transaction History Endpoint
@router.get("/transactions", response_model= list[TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transactions = (
        db.query(Transaction).filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions
