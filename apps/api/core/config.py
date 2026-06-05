from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    APP_SECRET_KEY: str = "supersecret32characterkeyforjwtencodinganddecoding"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    DATABASE_URL: str = "postgresql+asyncpg://shouko:supersecretpassword@localhost:5432/shouko"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    REDIS_URL: str = "redis://localhost:6379/0"

    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    RESEND_API_KEY: str = ""
    
    STRIPE_API_KEY: str = "mock-stripe-key"
    STRIPE_WEBHOOK_SECRET: str = "mock-webhook-secret"
    STRIPE_PRO_PRICE_ID: str = "price_mockpropriceid"
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
