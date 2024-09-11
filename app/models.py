from sqlalchemy import Column, Integer, String, Boolean, Date
from util.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    """Additional Attributes"""
    first_name = Column(String, unique=False, nullable=False)
    dob = Column(Date, nullable=False)
    bio = Column(String, nullable=True)
    gender = Column(String(1), nullable=False)
    profile_complete = Column(Boolean, default=False)
