from fastapi import Depends
from util.helper import *
from app.schemas import *
from app.settings import PUBLIC, PRIVATE, MIDDLE

###############################################################
"""PUBLIC PERMISSION: NO ACCESS TOKEN REQUIRED"""
###############################################################

@app.post(PUBLIC + "credentials/create")
async def save_credentials(cred: Credentials, db: AsyncSession = Depends(get_db)):
    new_user = User(
        email=cred.email,
        hashed_password=auther.hash(cred.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.post(PUBLIC + "credentials/tokens", response_model=TokenData)
async def credentials_to_tokens(cred: Credentials, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == cred.email))
    row = result.scalars().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not auther.equals(row.hashed_password, cred.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = {"id":row.id, "email":row.email}
    access_token = auther.generate_access_jwt(payload)
    refresh_token = auther.generate_refresh_jwt(payload)
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    return data

###############################################################
"""MIDDLE PERMISSION: ACCESS TOKEN REQUIRED"""
###############################################################

@app.get(MIDDLE + "users/all", response_model=List[ProfileOut])
async def get_all_users(request: Request, db: AsyncSession = Depends(get_db)):
    _ = await header_to_user_id(request)
    users = (await db.execute(select(User))).scalars().all()
    return users

###############################################################
"""PRIVATE PERMISSION: USER-INFER FROM ACCESS TOKEN REQUIRED"""
###############################################################

@app.get(PRIVATE + "tokens/refresh", response_model=TokenData)
async def get_access_from_refresh(request: Request):
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

@app.get(PRIVATE + "self", response_model=ProfileOut)
async def get_user_profile(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await header_to_user_object(request, db)
    return current_user
