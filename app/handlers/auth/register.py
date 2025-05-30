"""
User registration endpoint handler module.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.schemas import RegisterCredentials, PrivateProfileOut, ProfileBase
from app.models import User, Profile
from util.helper import get_auther
from util.auth import Auther
from util.db import get_db
from util.emailer import send_account_verification_email
from app.settings import (
    REQUIRE_USERS_VERIFIED,
    DEFAULT_2FA_ON,
)

async def register(
    req: RegisterCredentials, 
    db: AsyncSession = Depends(get_db),
    auther: Auther = Depends(get_auther),
    require_verified: bool = REQUIRE_USERS_VERIFIED
) -> PrivateProfileOut:
    """Register a new user with email and password"""
    # Create User record
    new_user = User(
        email=req.email,
        hashed_password=auther.hash(req.password),
        is_verified=False,
        require_2fa=DEFAULT_2FA_ON,
    )
    db.add(new_user)
    await db.flush()  # Generate user.id without committing
    
    new_profile = Profile(
        id=new_user.id,
        name=req.name
    )
    db.add(new_profile)
    
    await db.commit()
    await db.refresh(new_user)
    await db.refresh(new_profile)
    
    if require_verified:
        verification_url = auther.generate_email_verification_url(req.email)
        try:
            send_account_verification_email(
                to=req.email,
                verification_link=verification_url,
            )
            print(f"Verification email sent to {req.email}")
        except Exception as e:
            print(f"Error sending verification email: {str(e)}")
    
    return PrivateProfileOut(
        id=new_user.id,
        email=new_user.email,
        is_verified=new_user.is_verified,
        require_2fa=new_user.require_2fa,
        created_at=new_user.created_at,
        profile=ProfileBase(
            name=new_profile.name
        )
    )