from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_SECRET_KEY: str = "dev-secret-change-in-production"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/investment_research"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o"

    FMP_API_KEY: str = ""
    ALPHA_VANTAGE_KEY: str = ""

    DATA_PROVIDER: str = "mock"

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-production-domain.com",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
