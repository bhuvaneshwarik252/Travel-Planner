from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib
from config.settings import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def _normalize_secret(secret: str) -> str:
    b = secret.encode("utf-8")
    if len(b) > 72:
        # bcrypt has a 72-byte limit; pre-hash with SHA-256 to avoid
        # silent truncation and errors. Use hex digest (64 chars).
        return hashlib.sha256(b).hexdigest()
    return secret

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(_normalize_secret(plain_password), hashed_password)

def get_password_hash(password):
    return pwd_context.hash(_normalize_secret(password))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
