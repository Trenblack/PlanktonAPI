import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", default="secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Endpoints
PERMISSIONS = {
    "private": "me",
    "middle": "mid",
    "public": "api"
}
