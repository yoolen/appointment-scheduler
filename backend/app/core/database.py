"""
Database connection and session management using SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

# Create database engine
# echo=True enables SQL logging (useful for development)
engine = create_engine(settings.database_url, echo=True)  # Set to False in production

# Create SessionLocal class for database sessions
# Each instance will be a database session
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit transactions
    autoflush=False,  # Don't auto-flush changes
    bind=engine,  # Bind to our database engine
)


def get_db():
    """
    Dependency function to get database session.
    This will be used in FastAPI dependency injection.
    Ensures session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db  # FastAPI will inject this session
    finally:
        db.close()  # Always close the session
