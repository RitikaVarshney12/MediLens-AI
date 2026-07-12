from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MediLens AI"
    ENVIRONMENT: str = "development"

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"

    GEMINI_API_KEY: str = ""

    STORAGE_BUCKET: str = "medical-reports"
    MAX_UPLOAD_SIZE_MB: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()