from fastapi import FastAPI, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from contextlib import asynccontextmanager
from .auth import Auther
from .db import create_db_tables, get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    yield

app = FastAPI(lifespan=lifespan)
auther = Auther()

def header_to_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header is None or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split(" ")[1]
    return token

def token_to_user_id(token: str):
    decoded = auther.validate_access_jwt(token)
    if not decoded.get("is_valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=decoded.get("error", "Invalid Token"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = decoded.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in token"
        )
    return user_id

async def token_to_user_object(token: str, db: AsyncSession):
    user_id = token_to_user_id(token)
    result = await db.execute(select(User).filter(User.id == user_id))
    row = result.scalars().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return row

async def header_to_user_id(request: Request):
    token = header_to_token(request)
    current_user_id = token_to_user_id(token)
    return current_user_id

async def header_to_user_object(request: Request, db: AsyncSession):
    token = header_to_token(request)
    current_user_object = await token_to_user_object(token, db)
    return current_user_object
