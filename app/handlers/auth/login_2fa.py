from fastapi import HTTPException, status, Depends, Request
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.schemas import TwoFactorVerifyRequest, LoginResponse
from app.models import User
from util.db import get_db
from util.helper import partial_token_header_to_user_id
from util.auth import Auther
from util.helper import get_auther

async def login_2fa(
    request: Request,
    cred: TwoFactorVerifyRequest,
    auther: Auther = Depends(get_auther),
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Authenticate user and return either full or partial token depending on 2FA requirement."""
    # This will validate the partial token and return the user id
    user_id = partial_token_header_to_user_id(request)
    
    result = await db.execute(
        select(User).options(joinedload(User.two_factor)).filter(User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.two_factor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No 2FA code found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2) Code must be correct and not expired
    if cred.code != user.two_factor.code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong code",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.two_factor.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Code expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3) Generate full tokens
    payload = {"id": str(user.id), "email": user.email}
    access_token = auther.generate_access_jwt(payload)
    refresh_token = auther.generate_refresh_jwt(payload)

    return LoginResponse(
        requires_2fa=False,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
