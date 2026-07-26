#Import SQLAlchemy functions for database connection and ORM
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#Database connection URL
DATABASE_URL = "sqlite:///./bank.db"
# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args = {"check_same_thread": False}
)

#Create a session factory
SessionLocal = sessionmaker(
    autocommit = False,   # Changes are saved only after commit()
    autoflush = False,    # SQLAlchemy won't automatically flush changes
    bind = engine         #  Bind the session to our database engine
)
# Base class for all database models
Base = declarative_base()

# Dependency function for FastAPI --Provides a database session to API endpoints
def get_db():
    db = SessionLocal()
    try:
        # Give the session to the API endpoint
        yield db
    finally:
        db.close()