from pydantic import BaseModel, EmailStr, validator


class LoginInfo(BaseModel):
    email: EmailStr
    password: str

    @validator("email")
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

    @validator("password")
    def validate_password(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("Password must not be empty")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
