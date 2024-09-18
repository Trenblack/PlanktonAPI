from sqlalchemy import (
    Column, Integer, String, Boolean, Date,
    ForeignKey
)
from util.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

class Profile(Base):
    __tablename__ = "profiles"

    uid = Column(Integer, ForeignKey("users.id"), primary_key=True)

    """ADDITIONAL ATTRIBUTES"""
    first_name = Column(String, unique=False)
