from pydantic import BaseModel, EmailStr, ConfigDict, StringConstraints
from datetime import date
from typing import Optional, Annotated, List

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class Credentials(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]

class ProfileOut(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
