from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# User Table
# Represents the users table in the database.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    username = Column(String, unique = True, nullable = False)
    mobile = Column(String, unique = True, nullable = False)
    password_hash = Column(String, nullable = False)
    balance = Column(Float, default = 0)
    
    # Relationship with Transaction table-- One user can have many transactions.
    transactions = relationship("Transaction", back_populates="user")

# Transaction Table
# Stores all banking transactions.
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    counterparty_username = Column(String, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to User table
    user = relationship("User", back_populates="transactions")
