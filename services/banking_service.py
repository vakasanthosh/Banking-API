from app.models import User,Transaction, Card
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas import DepositRequest, WithdrawRequest, TransferRequest
from datetime import datetime

# Get Balance Service
# Returns the logged-in user's account balance.
def get_balance_service(current_user: User):
    return {
        "username": current_user.username,
        "balance": current_user.balance
    }

# Deposit Service
# Validates card details and deposits money into the user's account.
def deposit_service(
    db: Session,
    current_user: User,
    deposit: DepositRequest
):
        # Store current user for readability
        user = current_user
        # Check whether the card already exists
        card = db.query(Card).filter(
            Card.user_id == user.id,
            Card.card_number == deposit.card_number
        ).first()

        # Validate card holder name
        if deposit.card_holder_name.strip() == "":
            raise HTTPException(
              status_code=400,
              detail="Card holder name cannot be empty"
            )
        
        # Validate card number
        if not deposit.card_number.isdigit() or len(deposit.card_number) != 16:
            raise HTTPException(
              status_code=400,
              detail="Card number must contain exactly 16 digits"
            )

        # Validate CVV
        if not deposit.cvv.isdigit() or len(deposit.cvv) != 3:
            raise HTTPException(
              status_code=400,
              detail="CVV must contain exactly 3 digits"
            )
    
        # Validate expiry date
        if deposit.expiry_date.strip() == "":
            raise HTTPException(
              status_code=400,
              detail="Expiry date cannot be empty"
            )
        # Check expiry date format and whether the card has expired
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
        
        # Deposit amount must be positive
        if deposit.amount <= 0:
            raise HTTPException(
               status_code=400,
               detail="Amount must be greater than zero"
            )
        print(user)
        # Verify user exists
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not Found"
            )
        if not card:
            card = Card(
                user_id=user.id,
                card_holder_name=deposit.card_holder_name,
                card_number=deposit.card_number,
                cvv=deposit.cvv,
                expiry_date=deposit.expiry_date
            )

            db.add(card)
            db.commit()
            db.refresh(card)
        # Add deposit amount to balance
        user.balance += deposit.amount
    
        # Record deposit transaction
        transaction = Transaction(
            user_id = user.id,
            card_id=card.id,    
            transaction_type="Deposit",
            amount=deposit.amount
        )
        # Save transaction and balance
        db.add(transaction)
        db.commit()
        db.refresh(user)

        return{
            "message": "Deposit Successful",
            "balance": user.balance
        }

# Withdraw Service
# Withdraws money after validating balance and amount.
def withdraw_service(
        db: Session,
        current_user: User,
        withdraw: WithdrawRequest
):
        user = current_user
        card = db.query(Card).filter(
            Card.user_id == user.id,
            Card.card_number == withdraw.card_number
        ).first()
    
        # Check user exists
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
        if not card:
            raise HTTPException(
                status_code=404,
                detail="Card not found"
            )
        if (
            card.card_holder_name != withdraw.card_holder_name
            or card.cvv != withdraw.cvv
            or card.expiry_date != withdraw.expiry_date
        ):
           raise HTTPException(
               status_code=400,
               detail="Invalid card details"
            )
        # Ensure sufficient balance
        if withdraw.amount > user.balance:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance"
            )
        # Deduct amount
        user.balance -= withdraw.amount

        # Record withdrawal transaction
        transaction = Transaction(
            user_id=user.id,
            card_id=card.id,
            transaction_type="Withdraw",
            amount=withdraw.amount
        )
        # Save changes
        db.add(transaction)
        db.commit()
        db.refresh(user)
    
        return {
            "message": "Withdrawal Successful",
            "balance": user.balance
        }

# Transfer Service
# Transfers money from the logged-in user to another user.
def transfer_service(
    db: Session,
    current_user: User,
    transfer: TransferRequest
):
        # Sender is the logged-in user
        sender = current_user
        
        # Find receiver using mobile number
        receiver = db.query(User).filter(
            User.mobile == transfer.receiver_mobile
        ).first()
     
        # Receiver must exist
        if not receiver:
            raise HTTPException(
                status_code=404,
                detail="Receiver not found"
            )
        # Prevent transferring to yourself
        if sender.id == receiver.id:
            raise HTTPException(
                status_code=400,
                detail="Cannot transfer to yourself"
            )
        # Amount must be positive
        if transfer.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than zero"
            )
        # Sender must have enough balance
        if transfer.amount > sender.balance:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance"
            )
     
        try:
            # Deduct money from sender
            sender.balance -= transfer.amount
            # Credit money to receiver
            receiver.balance += transfer.amount
            # Record sender transaction
            sender_transaction = Transaction(
                user_id=sender.id,
                transaction_type="TRANSFER_OUT",
                amount=transfer.amount,
                counterparty_username=receiver.username
            )

            # Record receiver transaction
            receiver_transaction = Transaction(
                user_id=receiver.id,
                transaction_type="TRANSFER_IN",
                amount=transfer.amount,
                counterparty_username=sender.username
            )
            # Save both transactions 
            db.add(sender_transaction)
            db.add(receiver_transaction)
            db.commit()
            db.refresh(sender)
            db.refresh(receiver)
     
        except Exception as e:
            # Undo changes if any error occurs
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