from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # ===== Database =====
    DATABASE_URL: str

    # ===== Redis =====
    REDIS_URL: str

    # ===== JWT =====
    JWT_SECRET: str
    JWT_REFRESH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ===== App =====
    ENVIRONMENT: str = "development"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # ===== CORS =====
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ]

    # ===== Security =====
    BCRYPT_ROUNDS: int = 12
    RATE_LIMIT_LOGIN: int = 5      # محاولات في الدقيقة
    RATE_LIMIT_REGISTER: int = 3   # محاولات في الساعة

    # ===== Trading =====
    DEFAULT_VIRTUAL_BALANCE: float = 10000.0
    TRADING_FEE_PERCENT: float = 0.001   # 0.1%
    MAX_ORDER_QUANTITY: int = 10000
    MIN_ORDER_QUANTITY: float = 0.0001

    # ===== Email (SMTP) =====
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@adx-shares.com"
    EMAIL_VERIFICATION_REQUIRED: bool = True

    # ===== Market Data =====
    MARKET_DATA_PROVIDER: str = "mock"   # "mock" | "alphavantage" | "binance"
    ALPHA_VANTAGE_API_KEY: str = "demo"
    PRICE_UPDATE_INTERVAL_SECONDS: int = 300   # 5 دقائق

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()