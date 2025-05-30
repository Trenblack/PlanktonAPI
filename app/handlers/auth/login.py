from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from util.emailer import send_2fa_email
from app.schemas import LoginCredentials, LoginResponse
from app.models import User, TwoFactorAuthCode
from util.helper import get_auther
from util.auth import Auther
from util.db import get_db
from app.settings import REQUIRE_USERS_VERIFIED


async def login(
    cred: LoginCredentials, 
    db: AsyncSession = Depends(get_db),
    auther: Auther = Depends(get_auther),
    require_verified: bool = REQUIRE_USERS_VERIFIED
) -> LoginResponse:
    """Authenticate user and return either full or partial token depending on 2FA requirement."""
    # 1) Retrieve user by email
    result = await db.execute(select(User).filter(User.email == cred.email))
    row = result.scalars().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 2) Check password
    if not auther.equals(row.hashed_password, cred.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3) Check if verified
    if require_verified and not row.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4) If user requires 2FA, return a "partial" token, create and send 2FA code
    if row.require_2fa:
        payload = {"id": str(row.id), "email": row.email}
        partial_token = auther.generate_partial_jwt(payload)
        
        # Store needed values before DB operations
        user_email = row.email
        code = auther.generate_2fa_code()
        
        # Do all DB operations
        existing_code = await db.execute(select(TwoFactorAuthCode).filter(TwoFactorAuthCode.id == row.id))
        existing_code = existing_code.scalars().first()
        if existing_code:
            await db.delete(existing_code)
            await db.commit()
        
        two_factor = TwoFactorAuthCode(
            id=row.id,
            code=code
        )
        db.add(two_factor)
        await db.commit()
        await db.refresh(two_factor)

        # Email sending completely separate from DB operations
        try:
            send_2fa_email(to=user_email, code=code)
            print(f"2FA code sent to {user_email}")
        except Exception as e:
            print(f"Error sending 2FA code email: {str(e)}")

        return LoginResponse(
            requires_2fa=True,
            partial_token=partial_token,
        )

    # 5) Otherwise, return full tokens
    payload = {"id": str(row.id), "email": row.email}
    access_token = auther.generate_access_jwt(payload)
    refresh_token = auther.generate_refresh_jwt(payload)

    return LoginResponse(
        requires_2fa=False,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
