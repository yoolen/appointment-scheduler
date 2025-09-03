"""
Application configuration using Pydantic settings.
Reads from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database settings
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@postgres:5432/appointment_scheduler"
    )

    # Redis settings
    redis_url: str = "redis://redis:6379/0"

    # API settings
    cors_origins: str = "http://localhost:3000"

    # JWT settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    class Config:
        # Look for .env file to load environment variables
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()
