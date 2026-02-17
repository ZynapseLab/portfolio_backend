from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "portfolio_chatbot"

    JWT_SECRET: str = "change-me"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "anthropic/claude-3.5-sonnet"
    OPENROUTER_CLASSIFIER_MODEL: str = "openai/gpt-4o-mini"

    OPENAI_API_KEY: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    JONATHAN_EMAIL: str = ""
    PABLO_EMAIL: str = ""

    CORS_ORIGINS: list[str] = ["http://localhost:4321"]

    CHAT_DAILY_LIMIT: int = 10
    EMAIL_DAILY_LIMIT: int = 2

    LOG_FILE_PATH: str = "./logs/app.log"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def validate_required(self) -> None:
        errors = []
        if self.JWT_SECRET == "change-me":
            errors.append("JWT_SECRET must be set to a secure random value")
        if not self.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is required")
        if not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        if errors:
            raise ValueError(
                "Missing required configuration:\n" + "\n".join(f"  - {e}" for e in errors)
            )


settings = Settings()
