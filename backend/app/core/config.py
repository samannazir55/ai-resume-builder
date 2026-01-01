
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Project Settings ---
    PROJECT_NAME: str = "AI CV Builder"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # --- Database Settings ---
    # We provide a default for safety, but it should read from .env
    DATABASE_URL: str = "sqlite:///./cv_builder_local.db"

    # --- Security ---
    JWT_SECRET_KEY: str = "unsafe-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # --- ADMIN ---
    # Defines who can upload templates
    ADMIN_EMAIL: str = "admin@example.com"

    # --- AI BRAIN KEYS (The Missing VIPs) ---
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # --- Legacy/Optional ---
    HUGGING_FACE_TOKEN: Optional[str] = None

    # --- CONFIGURATION ---
    # This magic line tells Pydantic: 
    # "Read .env file" AND "Ignore any extra variables you don't know about"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"  # <--- THIS STOPS THE CRASH
    )

settings = Settings()

def get_settings() -> Settings:
    return settings
