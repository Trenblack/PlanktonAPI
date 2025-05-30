from argon2 import PasswordHasher
from datetime import datetime, timedelta, timezone
import jwt
import string
import random
from app.settings import (
    SECRET_KEY, 
    JWT_ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    REFRESH_TOKEN_EXPIRE_DAYS,
    EMAIL_VERIFICATION_EXPIRE_MINUTES,
    PARTIAL_TOKEN_EXPIRE_MINUTES,
    CLIENT_BASE_URL
)

hasher = PasswordHasher()

class Auther:
    """
    Authentication utility class for handling password hashing and JWT operations.
    """
    def __init__(self):
        self.hasher = PasswordHasher()

    def hash(self, text):
        """Hash a password using Argon2"""
        return self.hasher.hash(text)

    def equals(self, text1, text2):
        """Verify if a plaintext matches a hash"""
        result = False
        try:
            result = self.hasher.verify(text1, text2)
        except:
            result = False
        return result

    #######################################
    # TOKEN GENERATION METHODS
    #######################################

    def generate_partial_jwt(self, payload: dict) -> str:
        """Generate a short-lived token indicating 2FA is still needed."""
        payload_copy = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=PARTIAL_TOKEN_EXPIRE_MINUTES)
        payload_copy.update({"exp": expire, "type": "partial"})
        encoded = jwt.encode(payload_copy, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded
        
    def generate_access_jwt(self, payload):
        """Generate an access token with standard expiration time."""
        payload_copy = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload_copy.update({"exp": expire, "type":"access"})
        encoded = jwt.encode(payload_copy, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded
    
    def generate_email_verify_jwt(self, payload):
        """Generate an email verification token."""
        payload_copy = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=EMAIL_VERIFICATION_EXPIRE_MINUTES)
        payload_copy.update({"exp": expire, "type":"email"})
        encoded = jwt.encode(payload_copy, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded

    def generate_refresh_jwt(self, payload):
        """Generate a long-lived refresh token."""
        payload_copy = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload_copy.update({"exp": expire, "type":"refresh"})
        encoded = jwt.encode(payload_copy, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded
        
    def generate_email_verification_url(self, email):
        """Generate a complete URL for email verification."""
        payload = {"email": email}
        token = self.generate_email_verify_jwt(payload)
        return f"{CLIENT_BASE_URL}/verify-email?token={token}"
        
    def generate_2fa_code(self):
        """Generate a 6-digit alphanumeric uppercase code for 2FA verification."""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(6))

    #######################################
    # TOKEN VALIDATION METHODS
    #######################################

    def validate_partial_jwt(self, token):
        """Validate a partial token used for 2FA flow."""
        response = dict()
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if decoded.get("type") == "partial":
                response.update({"is_valid":True})
                response.update(decoded)
            else:
                response.update({"is_valid":False, "error": "Wrong Token Type"})
        except jwt.ExpiredSignatureError:
            response.update({"is_valid":False, "error": "Partial token has expired"})
        except jwt.InvalidTokenError:
            response.update({"is_valid":False, "error": "Invalid partial token"})
        return response

    def validate_access_jwt(self, token):
        """Validate an access token."""
        response = dict()
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if decoded.get("type") == "access":
                response.update({"is_valid":True})
                response.update(decoded)
            else:
                response.update({"is_valid":False, "error": "Wrong Token Type"})
        except jwt.ExpiredSignatureError:
            response.update({"is_valid":False, "error": "Access token has expired"})
        except jwt.InvalidTokenError:
            response.update({"is_valid":False, "error": "Invalid access token"})
        return response

    def validate_email_verify_jwt(self, token):
        """Validate an email verification token."""
        response = dict()
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if decoded.get("type") == "email":
                response.update({"is_valid":True})
                response.update(decoded)
            else:
                response.update({"is_valid":False, "error": "Wrong Token Type"})
        except jwt.ExpiredSignatureError:
            response.update({"is_valid":False, "error": "Email verification token has expired"})
        except jwt.InvalidTokenError:
            response.update({"is_valid":False, "error": "Invalid email verification token"})
        return response

    def validate_refresh_jwt(self, token):
        """Validate a refresh token and generate a new access token if valid."""
        response = dict()
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if decoded.get("type") == "refresh":
                new_access_jwt = self.generate_access_jwt(decoded)
                response.update({"is_valid": True, "access_token": new_access_jwt})
            else:
                response.update({"is_valid":False, "error": "Wrong Token Type"})
        except jwt.ExpiredSignatureError:
            response.update({"is_valid": False, "error": "Refresh token has expired"})
        except jwt.InvalidTokenError:
            response.update({"is_valid": False, "error": "Invalid refresh token"})
        return response
