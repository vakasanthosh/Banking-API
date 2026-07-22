from app.models import User,Transaction
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas import DepositRequest, WithdrawRequest, TransferRequest
from datetime import datetime

def get_balance_service(current_user: User):
    return {
        "username": current_user.username,
        "balance": current_user.balance
    }

def deposit_service(
    db: Session,
    current_user: User,
    deposit: DepositRequest
):
        user = current_user
        if deposit.card_holder_name.strip() == "":
            raise HTTPException(
              status_code=400,
              detail="Card holder name cannot be empty"
            )
    
        if not deposit.card_number.isdigit() or len(deposit.card_number) != 16:
            raise HTTPException(
              status_code=400,
              detail="Card number must contain exactly 16 digits"
            )
    
        if not deposit.cvv.isdigit() or len(deposit.cvv) != 3:
            raise HTTPException(
              status_code=400,
              detail="CVV must contain exactly 3 digits"
            )
    
        if deposit.expiry_date.strip() == "":
            raise HTTPException(
              status_code=400,
              detail="Expiry date cannot be empty"
            )
        try:
            expiry = datetime.strptime(deposit.expiry_date, "%m/%y")
            current = datetime.now()
            if expiry < current.replace(day=1):
                raise HTTPException(
                    status_code=400,
                    detail="Card has expired"
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Expiry date must be in MM/YY format"
            )
        
        if deposit.amount <= 0:
            raise HTTPException(
               status_code=400,
               detail="Amount must be greater than zero"
            )
        print(user)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not Found"
            )
        if deposit.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail= "Amount must be greater than zero"
            )
        user.balance += deposit.amount
    
        transaction = Transaction(
            user_id = user.id,
            type="Deposit",
            amount = deposit.amount
        )
        db.add(transaction)
        db.commit()
        db.refresh(user)
        return{
            "message": "Deposit Successful",
            "balance": user.balance
        }

def withdraw_service(
        db: Session,
        current_user: User,
        withdraw: WithdrawRequest
):
        user = current_user
    
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
    
        if withdraw.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than zero"
            )
    
        if withdraw.amount > user.balance:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance"
            )
    
        user.balance -= withdraw.amount
    
        transaction = Transaction(
            user_id=user.id,
            type="Withdraw",
            amount=withdraw.amount
        )
    
        db.add(transaction)
        db.commit()
        db.refresh(user)
    
        return {
            "message": "Withdrawal Successful",
            "balance": user.balance
        }

def transfer_service(
    db: Session,
    current_user: User,
    transfer: TransferRequest
):
        sender = current_user
         
        receiver = db.query(User).filter(
            User.mobile == transfer.receiver_mobile
        ).first()
     
        if not receiver:
            raise HTTPException(
                status_code=404,
                detail="Receiver not found"
            )
        if sender.id == receiver.id:
            raise HTTPException(
                status_code=400,
                detail="Cannot transfer to yourself"
            )
        if transfer.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than zero"
            )
        if transfer.amount > sender.balance:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance"
            )
     
        try:
            sender.balance -= transfer.amount
            receiver.balance += transfer.amount
            sender_transaction = Transaction(
                user_id=sender.id,
                type="TRANSFER_OUT",
                amount=transfer.amount,
                counterparty_username=receiver.username
            )
            receiver_transaction = Transaction(
                user_id=receiver.id,
                type="TRANSFER_IN",
                amount=transfer.amount,
                counterparty_username=sender.username
            )
             
            db.add(sender_transaction)
            db.add(receiver_transaction)
            db.commit()
     
        except Exception as e:
            db.rollback()
            print(e)
            raise HTTPException(
                status_code=500,
                detail="Transfer failed"
            )
     
        return {
            "message": "Transfer Successful",
            "sender_balance": sender.balance
        }