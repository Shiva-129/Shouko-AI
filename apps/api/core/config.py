from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


REQUIRED_SECRETS: list[str] = [
    "APP_SECRET_KEY",
    "DATABASE_URL",
    "OPENROUTER_API_KEY",
]


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    APP_SECRET_KEY: str = ""
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    DATABASE_URL: str = ""
    STORAGE_DIR: str = "./scratch/storage"

    REDIS_URL: str = ""

    OPENROUTER_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode="after")
    def validate_secrets(self):
        if self.ENVIRONMENT == "test":
            return self

        missing = []
        for secret in REQUIRED_SECRETS:
            if not getattr(self, secret, ""):
                missing.append(secret)

        if missing:
            msg = f"Missing required environment variables: {', '.join(missing)}"
            print(f"[Config] FATAL: {msg}")
            print(f"[Config] Create a .env file or set environment variables for: {', '.join(missing)}")
            raise RuntimeError(msg)

        return self


settings = Settings()
