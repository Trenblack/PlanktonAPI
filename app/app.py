from util.helper import *
from .schemas import *
from fastapi import Depends
from util.db import get_db
from util.settings import PERMISSIONS

###############################################################
"""PUBLIC PERMISSION: NO ACCESS TOKEN REQUIRED"""
###############################################################

@app.post("/{}/register/".format(PERMISSIONS["public"]))
async def register_user(user: UserRegistration, db: AsyncSession = Depends(get_db)):
    new_user = User(
        email=user.email,
        first_name = user.first_name,
        hashed_password=auther.hash(user.password),
        dob=user.dob,
        bio=user.bio,
        gender=user.gender,
        profile_complete = False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.post("/{}/tokens".format(PERMISSIONS["public"]))
async def get_tokens(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user.email))
    row = result.scalars().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not auther.equals(row.hashed_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auther.generate_access_jwt({"id": row.id, "email": row.email})
    refresh_token = auther.generate_refresh_jwt({"id": row.id, "email": row.email})
    data = {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }
    return data

###############################################################
"""MIDDLE PERMISSION: ACCESS TOKEN REQUIRED"""
###############################################################

@app.post("/{}/tokens/refresh".format(PERMISSIONS["middle"]))
async def get_access_from_refresh(request: Request):
    refresh_token = header_to_token(request)
    is_valid, data = auther.refresh_to_access(refresh_token)
    if is_valid:
        data["refresh_token"] = refresh_token
        data["token_type"] = "bearer"
        return data
    return {
        "error": "can't get access from refresh"
    }

###############################################################
"""PRIVATE PERMISSION: USER-INFER FROM ACCESS TOKEN REQUIRED"""
###############################################################

@app.get("/{}/profile".format(PERMISSIONS["private"]), response_model=UserProfilePublic)
async def get_user_profile(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await header_to_user_object(request, db)
    return current_user
