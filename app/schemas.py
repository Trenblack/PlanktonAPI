from pydantic import BaseModel, EmailStr, ConfigDict, StringConstraints
from datetime import date
from typing import Optional, Annotated

class UserRegistration(BaseModel):
    email: EmailStr
    first_name: Annotated[str, StringConstraints(min_length=1, max_length=50)]
    password: Annotated[str, StringConstraints(min_length=8)]
    dob: date
    bio: Optional[str] = None
    gender: Annotated[str, StringConstraints(pattern=r'^[MFN]$')]

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]

class UserProfilePublic(BaseModel):
    email: EmailStr
    first_name: Annotated[str, StringConstraints(min_length=1, max_length=50)]
    dob: date
    bio: Optional[str] = None
    gender: Annotated[str, StringConstraints(pattern=r'^[MFN]$')]

    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
