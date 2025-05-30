import os
from dotenv import load_dotenv

load_dotenv()

"""JWT SETTINGS"""
SECRET_KEY = os.getenv("SECRET_KEY", default="secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default=60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", default=30))
PARTIAL_TOKEN_EXPIRE_MINUTES = int(os.getenv("PARTIAL_TOKEN_EXPIRE_MINUTES", default=5))
TWO_FACTOR_CODE_EXPIRE_MINUTES = int(os.getenv("TWO_FACTOR_CODE_EXPIRE_MINUTES", default=5))
PASSWORD_RESET_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", default=60))

"""DATABASE SETTINGS"""
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    default="sqlite+aiosqlite:///./test.db"
).replace("postgres://", "postgresql+asyncpg://")

"""IF USING EMAIL VERIFICATION. OTHERWISE, SAFE TO IGNORE."""
REQUIRE_USERS_VERIFIED = bool(os.getenv("REQUIRE_USERS_VERIFIED", default=False))
DEFAULT_2FA_ON = bool(os.getenv("DEFAULT_2FA_ON", default=False))
EMAIL_VERIFICATION_EXPIRE_MINUTES = int(os.getenv("EMAIL_VERIFICATION_EXPIRE_MINUTES", default=15))
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_SENDER_DOMAIN = os.getenv("EMAIL_SENDER_DOMAIN")
EMAIL_SENDER_NAME = os.getenv("EMAIL_SENDER_NAME")

"""NETWORK SETTINGS"""
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:3000",
    "http://0.0.0.0:5173",
]

API_BASE_URL = os.getenv("BASE_URL", "http://0.0.0.0:8000")
CLIENT_BASE_URL = os.getenv("CLIENT_BASE_URL", "http://localhost:5173")

CUSTOM_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "")
if CUSTOM_ORIGINS:
    ALLOWED_ORIGINS.extend([origin.strip() for origin in CUSTOM_ORIGINS.split(",")])
ALLOWED_ORIGINS = list(set(ALLOWED_ORIGINS)) # Deduplicates

"""API ROUTES"""
PUBLIC = "/api/"
PRIVATE = "/me/"
MIDDLE = "/mid/"
