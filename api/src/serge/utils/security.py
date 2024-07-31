import base64
import hashlib
import os

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from serge.models.settings import Settings

ALGORITHM = "HS256"
settings = Settings()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    salt_and_hash = base64.b64decode(hashed_password.encode("utf-8"))
    salt = salt_and_hash[:16]
    stored_password = salt_and_hash[16:]
    new_hashed_password = hashlib.scrypt(plain_password.encode("utf-8"), salt=salt, n=8192, r=8, p=1, dklen=64)
    return new_hashed_password == stored_password


def get_password_hash(password: str) -> str:
    salt = os.urandom(16)
    hashed_password = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=8192, r=8, p=1, dklen=64)
    salt_and_hash = salt + hashed_password
    return base64.b64encode(salt_and_hash).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.SERGE_SESSION_EXPIRY)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SERGE_JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SERGE_JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
