import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db, User
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    logger.debug(f"Starting password hashing for password length: {len(password)}")
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed_str = hashed.decode('utf-8')
        logger.debug(f"Password hashed successfully, hash length: {len(hashed_str)}")
        return hashed_str
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    logger.debug(f"Verifying password, plain length: {len(plain_password)}, hash length: {len(hashed_password)}")
    try:
        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        logger.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    logger.debug(f"Creating access token for data: {list(data.keys())}")
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        logger.debug(f"Token will expire at: {expire}")
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"JWT token created successfully, length: {len(encoded_jwt)}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise

def verify_token(token: str) -> Optional[str]:
    """Verify and decode a JWT token"""
    logger.debug(f"Verifying JWT token, length: {len(token)}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("JWT token missing 'sub' field")
            return None
        logger.debug(f"JWT token verified successfully for user: {username}")
        return username
    except JWTError as e:
        logger.warning(f"JWT token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying JWT token: {e}")
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user"""
    logger.debug("Getting current user from token")
    try:
        token = credentials.credentials
        logger.debug(f"Token received, length: {len(token)}")
        
        username = verify_token(token)
        if username is None:
            logger.warning("Token verification failed, raising 401")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"Looking up user in database: {username}")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            logger.warning(f"User not found in database: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"Current user retrieved successfully: {user.username} (ID: {user.id})")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password"""
    logger.debug(f"Authenticating user: {username}")
    try:
        # Look up user by username
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        logger.debug(f"User found: {user.username} (ID: {user.id})")
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Password verification failed for user: {username}")
            return None
        
        logger.debug(f"User authenticated successfully: {username}")
        return user
    except Exception as e:
        logger.error(f"Error during user authentication: {e}")
        return None 