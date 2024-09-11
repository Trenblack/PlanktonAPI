from argon2 import PasswordHasher
from datetime import datetime, timedelta
import jwt
from .settings import SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

hasher = PasswordHasher()

class Auther:
    def __init__(self):
        self.hasher = PasswordHasher()

    def hash(self, text):
        return self.hasher.hash(text)

    def equals(self, text1, text2):
        result = False
        try:
            result = self.hasher.verify(text1, text2)
        except:
            result = False
        return result

    def generate_access_jwt(self, payload):
        payload_copy = payload.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload_copy.update({"exp": expire, "type":"access"})
        encoded = jwt.encode(payload_copy, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded

    def generate_refresh_jwt(self, payload):
        payload_copy = payload.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload_copy.update({"exp": expire, "type":"refresh"})
        encoded = jwt.encode(payload_copy, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded

    def validate_access_jwt(self, token):
        response = dict()
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if decoded.get("type") == "access":
                response.update({"is_valid":True})
                response.update(decoded)
            else:
                response.update({"is_valid":True, "error": "Wrong Token Type"})
        except jwt.ExpiredSignatureError:
            response.update({"is_valid":True, "error": "Access token has expired"})
        except jwt.InvalidTokenError:
            response.update({"is_valid":True, "error": "Invalid access token"})
        return response

    def refresh_to_access(self, token):
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
