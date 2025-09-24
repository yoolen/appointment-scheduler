from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.users import User

"""
Authentication and authorization utilities.

  WORKFLOW:
  1. Registration/Login: Store salted and hashed passwords using bcrypt
  2. Successful login returns two tokens:
     - Short-lived JWT access token (15min) for API access
     - Long-lived refresh token (30 days) stored as httpOnly cookie
  3. API Access: Access token sent via Authorization: Bearer <token> header
  4. Token Refresh: When access token expires, refresh token (from httpOnly cookie) 
     is used to get new access token without re-authentication. This is handled
     automatically by the frontend when API calls return 401 errors by calling 
     the /refresh endpoint. If the refresh token is expired or invalid, the user 
     must log in again.
     - Store the hashed refresh token in the database for validation
  5. Security: Refresh tokens are hashed before database storage and rotated on use
"""


def authenticate_user(db: Session, email: str, password: str) -> None | User:
    """Validate credentials and return user object if valid."""
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def create_jwt_token(user_id: str, email: str) -> str:
    """Generate a JWT token for authenticated user."""
    now = datetime.now(ZoneInfo("UTC"))
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {"sub": user_id, "email": email, "iat": now, "exp": expire}

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: str, email: str) -> str:
    """Generate a refresh token for authenticated user."""
    now = datetime.now(ZoneInfo("UTC"))
    expire = now + timedelta(days=settings.refresh_token_expire_days)

    payload = {"sub": user_id, "email": email, "iat": now, "exp": expire}

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_jwt_token(token: str) -> dict | None:
    """Verify the provided JWT token and return payload if valid."""
    try:
        payload: dict = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def verify_refresh_token(db: Session, token: str) -> dict | None:
    """Verify the provided refresh token."""
    try:
        payload: dict = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        # Check if token exists in database and is not revoked
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        if (
            user is None
            or user.refresh_token_hash is None  # Revoked or never logged in
            or not bcrypt.checkpw(
                token.encode("utf-8"), user.refresh_token_hash.encode("utf-8")
            )
        ):
            return None

        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def hash_password(password: str) -> str:
    """Hash a plaintext password for secure storage."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
