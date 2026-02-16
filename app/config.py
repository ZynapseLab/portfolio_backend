"""Configuración de la aplicación."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno."""
    
    # MongoDB
    mongodb_uri: str
    mongodb_db_name: str = "portfolio_db"
    
    # OpenRouter
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 1
    
    # Email (SMTP)
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    smtp_from_email: str
    smtp_from_name: str = "Portfolio Team"
    
    # Contact Emails
    contact_email_jonathan: str
    contact_email_pablo: str
    
    # Rate Limits
    rate_limit_chat_messages: int = 10
    rate_limit_emails: int = 2
    
    # Logging
    log_dir: str = "logs"
    log_level: str = "INFO"
    
    # Application
    app_name: str = "Portfolio Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
