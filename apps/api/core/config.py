import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


REQUIRED_SECRETS: list[str] = [
    "APP_SECRET_KEY",
    "DATABASE_URL",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "OPENROUTER_API_KEY",
]

REQUIRED_PRODUCTION_SECRETS: list[str] = [
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "STRIPE_PRO_PRICE_ID",
    "RESEND_API_KEY",
    "REDIS_URL",
]


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    APP_SECRET_KEY: str = ""
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    REDIS_URL: str = ""

    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRO_PRICE_ID: str = ""
    FRONTEND_URL: str = "http://localhost:3000"

    SUPABASE_STORAGE_BUCKET: str = "papers"

    SENTRY_DSN: str = ""

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

        if self.ENVIRONMENT == "production":
            for secret in REQUIRED_PRODUCTION_SECRETS:
                if not getattr(self, secret, ""):
                    missing.append(secret)

        if missing:
            msg = f"Missing required environment variables: {', '.join(missing)}"
            print(f"[Config] FATAL: {msg}")
            print(f"[Config] Create a .env file or set environment variables for: {', '.join(missing)}")
            raise RuntimeError(msg)

        return self


settings = Settings()
