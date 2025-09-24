from pydantic import BaseModel, EmailStr, field_validator


class LoginInfo(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    def normalize_email(self, v: str) -> str:
        return v.lower().strip()

    @field_validator("password")
    def validate_password(self, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("Password must not be empty")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
