from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from app.settings import DATABASE_URL

SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, autocommit=False, autoflush=False) # type: ignore

Base: DeclarativeMeta = declarative_base()

async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session: # type: ignore
        try:
            yield session
        finally:
            await session.close()
