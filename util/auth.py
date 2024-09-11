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
        # access -> Status,Id,Email
        data = [False, {}]  # valid:bool, payload:dict
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if decoded["type"] == "access":
                data = [True, decoded]
            else:
                data = [False, {"error": "Wrong Token Type"}]
        except jwt.ExpiredSignatureError:
            data = [False, {"error": "Access token has expired"}]
        except jwt.InvalidTokenError:
            data = [False, {"error": "Invalid access token"}]
        return data

    def refresh_to_access(self, token):
        # refresh -> access
        data = [False, {}]  # valid:bool, jwt:token
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if decoded["type"] == "refresh":
                new_access_jwt = self.generate_access_jwt(decoded)
                data = [True, {"access_token": new_access_jwt}]
            else:
                data = [False, {"error": "Wrong Token Type"}]
        except jwt.ExpiredSignatureError:
            data = [False, {"error": "Refresh token has expired"}]
        except jwt.InvalidTokenError:
            data = [False, {"error": "Invalid refresh token"}]
        return data
