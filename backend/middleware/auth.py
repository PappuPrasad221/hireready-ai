from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-for-development")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception

def get_current_user(user_id: str = Depends(verify_token)):
    """Get current authenticated user"""
    # In a real implementation, fetch user from database
    # For now, return mock user data
    return {
        "user_id": user_id,
        "email": f"user_{user_id}@example.com",
        "name": f"User {user_id}",
        "is_active": True
    }

# Optional authentication - allows requests without token but provides user if token exists
async def optional_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication - returns None if no token provided"""
    if not credentials:
        return None
    
    try:
        return verify_token(credentials)
    except HTTPException:
        return None

# Mock user database for development
MOCK_USERS = {
    "demo_user": {
        "user_id": "demo_user",
        "email": "demo@hireready.ai",
        "name": "Demo User",
        "password": "demo123",  # In production, use hashed passwords
        "is_active": True
    }
}

def authenticate_user(email: str, password: str):
    """Authenticate user credentials"""
    user = MOCK_USERS.get(email)
    if not user or user["password"] != password:
        return None
    return user

def get_current_user_optional(user_id: str = Depends(verify_token)):
    """Get current user with optional authentication"""
    return user_id
