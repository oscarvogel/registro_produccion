try:
    from pydantic_settings import BaseSettings
except Exception:
    # Fallback for environments with pydantic (v1) or missing pydantic_settings
    try:
        from pydantic import BaseSettings
    except Exception:
        raise

class Settings(BaseSettings):
    PROJECT_NAME: str = "registro_produccion"
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/dbname"
    ALLOWED_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    SECRET_KEY: str = "change-me-in-production-with-a-real-secret-key"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    class Config:
        env_file = ".env"

settings = Settings()
