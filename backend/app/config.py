import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "BrandRoots Governance Platform"
    APP_VERSION: str = "2.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    
    # Database
    # Default to sqlite:///./brandroots.db for seamless zero-dependency local verification
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./brandroots.db")
    
    # Auth / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "brandroots-hackathon-round2-inkloom-secret-key-vettriselvam190")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AI / LLM Configuration
    # Uses server-side API or deterministic fallback engine
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "hybrid_deterministic")  # openai, anthropic, gemini, or hybrid_deterministic
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    # Supabase (Optional for cloud deploy)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Security
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
    ALLOWED_EXTENSIONS: list[str] = [".txt", ".pdf", ".docx", ".md"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
