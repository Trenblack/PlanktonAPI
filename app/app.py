from fastapi import Depends
from util.helper import *
from util.settings import PERMISSIONS
from .schemas import *

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

@app.post("/{}/tokens".format(PERMISSIONS["public"]), response_model=TokenData)
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

@app.post("/{}/tokens/refresh".format(PERMISSIONS["middle"]), response_model=TokenData)
async def get_access_from_refresh(request: Request):
    refresh_token = header_to_token(request)
    response = auther.refresh_to_access(refresh_token)
    if not response["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token Invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    response["refresh_token"] = refresh_token
    response["token_type"] = "bearer"
    return response

###############################################################
"""PRIVATE PERMISSION: USER-INFER FROM ACCESS TOKEN REQUIRED"""
###############################################################

@app.get("/{}/profile".format(PERMISSIONS["private"]), response_model=UserProfilePublic)
async def get_user_profile(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await header_to_user_object(request, db)
    return current_user
