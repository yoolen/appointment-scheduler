from __future__ import annotations

import bcrypt
from sqlalchemy.orm import Session

from app.models.users import User


def authenticate_user(db: Session, username: str, password: str) -> None | User:
    """Validate credentials and return user object if valid."""
    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def create_jwt_token() -> str:
    """Generate a JWT token for authenticated user."""


def create_refresh_token() -> str:
    """Generate a refresh token for authenticated user."""


def verify_jwt_token() -> bool:
    """Verify the provided JWT token."""


def verify_refresh_token() -> bool:
    """Verify the provided refresh token."""


def hash_password(password: str) -> str:
    """Hash a plaintext password for secure storage."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
