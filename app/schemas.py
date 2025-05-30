from pydantic import BaseModel, EmailStr, ConfigDict, StringConstraints, Field, field_validator
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

# Common configuration for all models
class BaseConfig(BaseModel):
    """Base configuration class for all schemas"""
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model -> Pydantic model conversion
        populate_by_name=True  # Allow both alias and model field names
    )

class TokenData(BaseConfig):
    """Schema for authentication token data"""
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Type of token")
    
    model_config = ConfigDict(frozen=True)  # Tokens should be immutable

class RegisterCredentials(BaseConfig):
    """Schema for user registration data"""
    email: EmailStr = Field(description="User's email address")
    password: Annotated[str, StringConstraints(min_length=8)] = Field(
        description="Password with minimum length of 8 characters"
    )
    name: str = Field(description="User's full name")
    
    # Optional validation to verify password complexity
    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class LoginCredentials(BaseConfig):
    """Schema for user login data"""
    email: EmailStr = Field(description="User's email address")
    password: Annotated[str, StringConstraints(min_length=8)] = Field(
        description="Password with minimum length of 8 characters"
    )

class TwoFactorAuthCredentials(BaseConfig):
    """Schema for 2FA verification"""
    email: EmailStr = Field(description="User's email address")
    code: Annotated[str, StringConstraints(min_length=6, max_length=6)] = Field(
        description="6-digit alphanumeric uppercase verification code"
    )
    
    @field_validator('code')
    @classmethod
    def code_must_be_alphanumeric_uppercase(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('Code must contain only alphanumeric characters')
        if not v.isupper():
            raise ValueError('Code must be uppercase')
        return v

class ProfileBase(BaseConfig):
    """Base schema for profile data - matches Profile model"""
    name: str = Field(description="User's full name")
    # Add more profile fields as needed (bio, avatar, location, website, etc.)

class PublicUserBase(BaseConfig):
    """Base schema for user authentication data - matches User model"""
    id: UUID = Field(description="User ID (UUID)")
    email: EmailStr = Field(description="User's email address")
    is_verified: bool = Field(description="Whether the user's email is verified")
    
class PublicProfileOut(PublicUserBase):
    """Schema for limited public user profile information"""
    profile: ProfileBase = Field(..., description="User's profile information")
    
class PrivateUserBase(BaseConfig):
    """Base schema for user authentication data - matches User model"""
    id: UUID = Field(description="User ID (UUID)")
    email: EmailStr = Field(description="User's email address")
    is_verified: bool = Field(description="Whether the user's email is verified")
    require_2fa: bool = Field(description="Whether 2FA is required for this user")
    created_at: datetime = Field(description="When the user account was created")

class PrivateProfileOut(PrivateUserBase):
    """Schema for full privileged user profile information (self-view or admin-view)"""
    profile: ProfileBase = Field(..., description="User's profile information")

class VerificationResponse(BaseConfig):
    """Schema for email verification response"""
    verified: bool = Field(description="Whether the email was verified successfully")
    message: str = Field(description="Message providing details about the verification")

class LoginResponse(BaseConfig):
    """Schema for login response"""
    requires_2fa: bool = Field(description="Whether 2FA is required for this user")
    access_token: Optional[str] = Field(default=None, description="JWT access token")
    refresh_token: Optional[str] = Field(default=None, description="JWT refresh token") 
    partial_token: Optional[str] = Field(default=None, description="JWT partial token for 2FA flow")
    token_type: str = Field(default="bearer", description="Type of token")

class TwoFactorVerifyRequest(BaseConfig):
    """Schema for 2FA verification with partial token"""
    code: Annotated[str, StringConstraints(min_length=6, max_length=6)] = Field(
        description="6-digit alphanumeric uppercase verification code"
    )