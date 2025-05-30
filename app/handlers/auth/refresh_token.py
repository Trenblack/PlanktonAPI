"""
Token refresh endpoint handler module.
"""

from fastapi import HTTPException, Request, status, Depends
from app.schemas import TokenData
from util.helper import header_to_token, get_auther
from util.auth import Auther

async def refresh_token(
    request: Request,
    auther: Auther = Depends(get_auther)
) -> TokenData:
    """Generate a new access token using a valid refresh token"""
    refresh_token = header_to_token(request)
    response = auther.refresh_to_access(refresh_token)
    if not response.get("is_valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token Invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    response["refresh_token"] = refresh_token
    response["token_type"] = "bearer"
    return response 