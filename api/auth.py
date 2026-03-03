"""
Authentication and Security Layer
Implements JWT tokens, password hashing, and role-based access control
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
from models import User, UserRole


# ============================================================================
# Password Hashing
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT Token Management
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Payload data to encode
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


# ============================================================================
# Authentication Dependencies
# ============================================================================

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_db: dict = Depends(lambda: {})  # Will be injected with actual user database
) -> User:
    """
    Dependency to get the current authenticated user
    
    Args:
        credentials: Bearer token from request
        user_db: User database (injected)
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    resolved_user_db = user_db if user_db else user_database.get_all_users()

    user = resolved_user_db.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


def require_role(*allowed_roles: UserRole):
    """
    Decorator factory for role-based access control
    
    Args:
        allowed_roles: Roles that are allowed to access the endpoint
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(r.value for r in allowed_roles)}"
            )
        return current_user
    
    return role_checker


# ============================================================================
# User Database (In-Memory - would be replaced with real DB in production)
# ============================================================================

class UserDatabase:
    """In-memory user database for authentication"""
    
    def __init__(self):
        self._users: dict[str, User] = {}
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Create default users for each portal role"""
        # Default staff user: username=admin, password=admin123
        staff_user = User(
            username="admin",
            role=UserRole.STAFF,
            hashed_password=hash_password("admin123"),
            full_name="System Administrator",
            disabled=False
        )
        self._users["admin"] = staff_user

        # Default TA user: username=ta_demo, password=ta123456
        ta_user = User(
            username="ta_demo",
            role=UserRole.TA,
            hashed_password=hash_password("ta123456"),
            full_name="Demo Teaching Assistant",
            disabled=False
        )
        self._users["ta_demo"] = ta_user

        # Default student user: username=student_demo, password=student123
        student_user = User(
            username="student_demo",
            role=UserRole.STUDENT,
            hashed_password=hash_password("student123"),
            full_name="Demo Student",
            disabled=False
        )
        self._users["student_demo"] = student_user
    
    def add_user(self, username: str, password: str, role: UserRole, full_name: Optional[str] = None) -> User:
        """Add a new user to the database"""
        if username in self._users:
            raise ValueError(f"User {username} already exists")
        
        user = User(
            username=username,
            role=role,
            hashed_password=hash_password(password),
            full_name=full_name,
            disabled=False
        )
        self._users[username] = user
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """Retrieve a user by username"""
        return self._users.get(username)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        user = self.get_user(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def get_all_users(self) -> dict[str, User]:
        """Get all users (for dependency injection)"""
        return self._users
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        if username in self._users:
            del self._users[username]
            return True
        return False


# Global user database instance
user_database = UserDatabase()
