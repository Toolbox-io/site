import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
import random

import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from constants import CONTENT_PATH
from db.core import get_db, get_session_factory
from models import User, BlacklistedToken
from mail import send_mail, render_email

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Common passwords to block
COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "abc123", "password123", "admin", 
    "letmein", "welcome", "master", "hello", "freedom", "whatever", "qazwsx", 
    "trustno1", "iwantu", "love", "696969", "access", "computer", "654321", 
    "1qaz2wsx", "7777777", "121212", "11111111"
}

security = HTTPBearer()

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """ 

    if len(password) < 8:
        return False, "code 9: Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "code 10: Password must be less than 128 characters"
    
    # Check for common passwords
    if password.lower() in COMMON_PASSWORDS:
        return False, "code 11: Password is too common, please choose a stronger password"
    
    # Check for character variety
    has_chars = any((c.isupper() or c.islower()) for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not (has_chars and has_digit and has_special):
        return False, "code 12: Password must contain letters, digits, and special characters"
    
    return True, ""

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    logger.debug(f"Starting password hashing for password length: {len(password)}")
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed_str = hashed.decode('utf-8')
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
            expire = datetime.now() + timedelta(minutes=60 * 24 * 365) # 1 year
        to_encode.update({"exp": expire})
        logger.debug(f"Token will expire at: {expire}")
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"JWT token created successfully, length: {len(encoded_jwt)}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise

def is_token_blacklisted(token: str) -> bool:
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        return db.query(BlacklistedToken).filter_by(token=token).first() is not None
    finally:
        db.close()

def blacklist_token(token: str):
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        if not db.query(BlacklistedToken).filter_by(token=token).first():
            db.add(BlacklistedToken(token=token))
            db.commit()
    finally:
        db.close()

def verify_token(token: str) -> Optional[str]:
    logger.debug(f"Verifying JWT token, length: {len(token)}")
    if is_token_blacklisted(token):
        logger.warning("JWT token is blacklisted")
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
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
        user: User | None = db.query(User).filter(User.username == username).first()
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
        user: User | None = db.query(User).filter(User.username == username).first()
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        logger.debug(f"User found: {user.username} (ID: {user.id})")
        
        # Verify password
        if not verify_password(password, user.hashed_password): # TODO #13: compare password hashes instead of hashing the plaintext password in the request
            logger.warning(f"Password verification failed for user: {username}")
            return None
        
        logger.debug(f"User authenticated successfully: {username}")
        return user
    except Exception as e:
        logger.error(f"Error during user authentication: {e}")
        return None

def send_verify_email(user: User, db: Session):
    code = str(random.randint(1, 999999)).zfill(6)
    user.verification_code = code
    db.commit()
    html_body = render_email("verify", CODE=code)
    send_mail(
        user.email,
        "Подтвертите ваш email",
        html_body,
        html=True
    )