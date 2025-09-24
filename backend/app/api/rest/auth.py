from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ...core.auth import (
    authenticate_user,
    create_jwt_token,
    create_refresh_token,
    verify_jwt_token,
    verify_refresh_token,
)
from ...core.database import get_db
from ...models.users import User
from ..schemas.auth import LoginInfo

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login")
def login(
    info: LoginInfo, response: Response, db: Session = Depends(get_db)
) -> dict[str, str]:
    if user := authenticate_user(db, info.email, info.password):
        access_token = create_jwt_token(user.id, user.email)
        refresh_token = create_refresh_token(user.id, user.email)

        # Store refresh token in database
        user.refresh_token_hash = refresh_token
        db.commit()

        # Set httpOnly cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/",
            max_age=15 * 60 * 60,  # 15 minutes
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/",
            max_age=30 * 24 * 60 * 60,  # 30 days
        )

        return {"message": "Login successful"}

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/me")
def read_current_user(
    db: Session = Depends(get_db), access_token: str | None = Cookie(None)
) -> dict[str, str]:
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token provided")

    # Verify and decode the JWT token
    payload = verify_jwt_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Get user from database using the user_id from token
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": str(user.id), "email": user.email, "is_active": str(user.is_active)}


@router.get("/refresh")
def refresh_token(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(None),
) -> dict[str, str]:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    # Verify and decode the refresh token
    payload = verify_refresh_token(db, refresh_token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Generate a new access token
    user_id = payload["sub"]
    email = payload["email"]
    new_access_token = create_jwt_token(user_id, email)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=15 * 60,  # 15 minutes
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
    )

    return {"message": "Token refreshed successfully"}


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    """Log out the user by clearing authentication cookies."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
