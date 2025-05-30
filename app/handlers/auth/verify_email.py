from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas import VerificationResponse
from app.models import User
from util.auth import Auther
from util.helper import get_auther
from util.db import get_db

async def verify_email(
    token: str, 
    db: AsyncSession = Depends(get_db),
    auther: Auther = Depends(get_auther)
):
    """
    Verify a user's email address using the token sent to their email
    """
    token_data = auther.validate_email_verify_jwt(token)
    
    if not token_data.get("is_valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=token_data.get("error", "Invalid verification token")
        )
    
    email = token_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token, email not found"
        )
    
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return VerificationResponse(
            verified=True,
            message="Email already verified"
        )
    
    user.is_verified = True
    await db.commit()
    
    return VerificationResponse(
        verified=True,
        message="Email verified successfully"
    )
