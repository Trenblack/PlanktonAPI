from fastapi import FastAPI, HTTPException, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User, Profile
from contextlib import asynccontextmanager
from util.auth import Auther
from util.db import create_db_tables, get_db
import json
import uuid
import logging
from fastapi.responses import JSONResponse
from app.settings import REQUIRE_USERS_VERIFIED

# Configure central logger
logger = logging.getLogger("plankton-api")

#######################################
# JSON HANDLING
#######################################

# Custom JSON encoder to handle UUID objects
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # Return a string representation of the UUID
            return str(obj)
        return super().default(obj)

# Custom JSONResponse class that uses our encoder
class CustomJSONResponse(JSONResponse):
    """Custom JSON response that properly serializes UUIDs."""
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=UUIDEncoder,
        ).encode("utf-8")

#######################################
# APPLICATION LIFECYCLE
#######################################

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events for the FastAPI application.
    """
    # Setup logging
    logger.info("Starting up application")
    
    # Initialize database
    try:
        await create_db_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        # Continue startup even if database fails
    
    # Initialize authentication system
    try:
        logger.info("Initializing authentication helpers")
        app.state.auther = Auther()
        logger.info("Authentication helpers initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize authentication helpers: {str(e)}", exc_info=True)
        app.state.auther = None
    
    # Yield control back to FastAPI
    yield
    
    # Shutdown operations
    logger.info("Application shutdown initiated")
    logger.info("Shutting down application")

#######################################
# AUTHENTICATION HELPERS
#######################################
    
def get_auther(request: Request) -> Auther:
    """Dependency to get the Auther instance from app state"""
    auther = request.app.state.auther
    if auther is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication system is not initialized"
        )
    return auther

def header_to_token(request: Request):
    """Extract token from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if auth_header is None or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split(" ")[1]
    return token

#######################################
# TOKEN VALIDATION AND USER CHECKS
#######################################

async def access_token_header_to_user_id(request: Request, db: AsyncSession = Depends(get_db), verify_user: bool = REQUIRE_USERS_VERIFIED):
    """
    Validate access token and return user ID
    Optional verification of user's verified status if REQUIRE_USERS_VERIFIED is True
    """
    token = header_to_token(request)
    auther = get_auther(request)
    
    decoded = auther.validate_access_jwt(token)
    if not decoded.get("is_valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=decoded.get("error", "Invalid access token"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    validate_token_contents(decoded, expected_type="access")
    user_id = uuid.UUID(decoded.get("id"))
    
    # Check if user is verified when required
    if verify_user:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User email not verified"
            )
    
    return user_id

async def refresh_token_header_to_user_id(request: Request):
    """Validate refresh token and return user ID"""
    token = header_to_token(request)
    auther = get_auther(request)
    
    decoded = auther.validate_refresh_jwt(token)
    if not decoded.get("is_valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=decoded.get("error", "Invalid refresh token"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    validate_token_contents(decoded, expected_type="refresh")
    return uuid.UUID(decoded.get("id"))

async def partial_token_header_to_user_id(request: Request):
    """Validate partial token (for 2FA flow) and return user ID"""
    token = header_to_token(request)
    auther = get_auther(request)
    
    decoded = auther.validate_partial_jwt(token)
    if not decoded.get("is_valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=decoded.get("error", "Invalid partial token"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    validate_token_contents(decoded, expected_type="partial")
    return uuid.UUID(decoded.get("id"))

def validate_token_contents(decoded, expected_type=None):
    """Validate that token contains required fields and is of the expected type"""
    user_id = decoded.get("id")
    token_type = decoded.get("type")
    email = decoded.get("email")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in token"
        )

    if not token_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token type not found in token"
        )

    if expected_type and token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected {expected_type} token but got {token_type}"
        )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in token"
        )
    
    # Verify user_id is a valid UUID
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format in token"
        )
