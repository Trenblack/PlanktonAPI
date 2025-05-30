from fastapi import APIRouter
from app.settings import PUBLIC, PRIVATE

# Import centralized handlers
from app.handlers.auth import (
    register, login, refresh_token, 
    verify_email, login_2fa
)
from app.handlers.root import root

# Create router
router = APIRouter()

# HEALTH CHECK ROUTE
router.get("/")(root)

# API ROUTES
router.post(PUBLIC + "register")(register)
router.post(PUBLIC + "login")(login)
router.post(PUBLIC + "login-2fa")(login_2fa)
router.get(PRIVATE + "refresh")(refresh_token) 
router.get(PUBLIC + "verify-email")(verify_email)

# USER ROUTES