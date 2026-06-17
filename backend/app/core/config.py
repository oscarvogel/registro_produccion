from pathlib import Path

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
    APP_NAME: str = "registro_produccion"
    APP_INSTANCE: str = "local"
    APP_ENV: str = "development"
    APP_VERSION: str = "unknown"
    LOG_LEVEL: str = "info"
    # Add the frontend dev server origins (common ports 5173/5174 and 3000)
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://localhost:8005",
    ]
    ALLOWED_ORIGIN_REGEX: str = r"^http://(localhost|127\.0\.0\.1):\d+$"
    SECRET_KEY: str = "change-me-in-production-with-a-real-secret-key"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    class Config:
        # Load .env from the backend root regardless of process working directory.
        env_file = str(Path(__file__).resolve().parents[2] / ".env")

settings = Settings()
