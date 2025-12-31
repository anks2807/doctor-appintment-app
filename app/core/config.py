import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Default to a safe, but insecure key for development if not set.
    # For production, this MUST be set to a strong, random string.
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    ALGORITHM: str = "HS256"


settings = Settings()