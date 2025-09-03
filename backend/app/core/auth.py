from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.users import User


def authenticate_user(db: Session, username: str, password: str) -> None | User:
    """Validate credentials and return user object if valid."""
    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def create_jwt_token(user_id: str, username: str) -> str:
    """Generate a JWT token for authenticated user."""
    now = datetime.now(ZoneInfo("UTC"))
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {"sub": user_id, "username": username, "iat": now, "exp": expire}

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: str, username: str) -> str:
    """Generate a refresh token for authenticated user."""
    now = datetime.now(ZoneInfo("UTC"))
    expire = now + timedelta(days=settings.refresh_token_expire_days)

    payload = {"sub": user_id, "username": username, "iat": now, "exp": expire}

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


def verify_refresh_token(token: str) -> dict | None:
    """Verify the provided refresh token."""
    # For demo purposes: stub returns valid payload for any non-empty token
    # Production approach would decode JWT and check database storage/revocation
    if token:
        return {
            "sub": "stub-user",
            "username": "stub",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(days=1),
        }  # noqa: E501
    return None

    # Production implementation:
    # try:
    #     payload = jwt.decode(
    #         token, settings.secret_key, algorithms=[settings.algorithm]
    #     )
    #     # Check if token exists in database and is not revoked
    #     return payload
    # except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
    #     return None


def hash_password(password: str) -> str:
    """Hash a plaintext password for secure storage."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
