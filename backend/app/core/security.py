from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings

# Setup hashing engine
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password:
        return False
        
    # Safety Check: Bcrypt crashes if input > 72 bytes
    try:
        # Passlib handles some of this, but strict backends need manual truncation
        encoded = plain_password.encode('utf-8')
        if len(encoded) > 72:
            plain_password = encoded[:72].decode('utf-8', errors='ignore')
            
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        # Fallback for weird edge cases
        return False

def get_password_hash(password: str) -> str:
    # ✂️ THE FIX: Safety Truncation ✂️
    # Bcrypt cannot digest > 72 bytes. We clip it to stay safe.
    # This maintains security while preventing 500 server crashes.
    encoded = password.encode('utf-8')
    if len(encoded) > 72:
        password = encoded[:72].decode('utf-8', errors='ignore')
        
    return pwd_context.hash(password)

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
