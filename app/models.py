from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
import uuid
from util.db import Base
from app.settings import TWO_FACTOR_CODE_EXPIRE_MINUTES

class User(Base):
    __tablename__ = "users"

    """USER REQUIRED FIELDS. ONLY CHANGE THESE IF YOU KNOW WHAT YOU ARE DOING."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    require_2fa = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    two_factor = relationship("TwoFactorAuthCode", back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    
    """USER CUSTOMIZABLE FIELDS. FIRE AWAY."""
    name = Column(String, nullable=False)
    # ... bio, avatar, location, website, etc.
    
    # Relationships
    user = relationship("User", back_populates="profile")


class TwoFactorAuthCode(Base):
    __tablename__ = "two_factor_auth_codes"

    # Feel free to ignore if you don't plan on using 2FA.
    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    code = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(minutes=TWO_FACTOR_CODE_EXPIRE_MINUTES))
    
    # Relationships
    user = relationship("User", back_populates="two_factor")
