from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings

# Setup hashing engine with explicit backend configuration
# This prevents runtime backend detection issues
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Explicit rounds configuration
)

# Force backend initialization early to catch issues at startup
try:
    # Trigger backend loading with a safe test
    pwd_context.hash("test")
except Exception as e:
    print(f"Warning: Bcrypt backend initialization issue: {e}")
    # Fallback: try to set a specific backend
    try:
        import bcrypt
        pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12,
        )
    except ImportError:
        raise RuntimeError("Bcrypt library not properly installed") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
        
    # Safety Check: Bcrypt crashes if input > 72 bytes
    try:
        # Passlib handles some of this, but strict backends need manual truncation
        encoded = plain_password.encode('utf-8')
        if len(encoded) > 72:
            # Truncate to 72 bytes
            plain_password = encoded[:72].decode('utf-8', errors='ignore')
            
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, Exception) as e:
        # Log the error in production
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    IMPORTANT: Bcrypt cannot digest > 72 bytes. We truncate to stay safe.
    This maintains security while preventing 500 server crashes.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Truncate to 72 bytes for bcrypt compatibility
    encoded = password.encode('utf-8')
    if len(encoded) > 72:
        password = encoded[:72].decode('utf-8', errors='ignore')
    
    try:
        return pwd_context.hash(password)
    except Exception as e:
        # More detailed error for debugging
        raise RuntimeError(f"Password hashing failed: {str(e)}") from e


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


# Deployment Trigger Update: 1767356701.6331584