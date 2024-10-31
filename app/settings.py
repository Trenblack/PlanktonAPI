import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", default="secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    default="sqlite+aiosqlite:///./test.db"
).replace("postgres://", "postgresql+asyncpg://")

PUBLIC = "/api/"
PRIVATE = "/me/"
MIDDLE = "/mid/"
