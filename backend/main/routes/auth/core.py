import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse

from db.core import get_db
from limiter import limiter
from models import UserCreate, UserLogin, UserResponse, Token, User
from routes.auth.utils import send_verify_email, validate_password, hash_password, authenticate_user, create_access_token, get_current_user, security, blacklist_token

logger = logging.getLogger(__name__)

################
# Basic routes #
################
router = APIRouter()

@router.get("/login")
async def login(): return RedirectResponse("/account/login", status_code=308)

@router.get("/register")
async def register(): return RedirectResponse("/account/register", status_code=308)


##############
# API routes #
##############
api_router = APIRouter()

# Core
@api_router.post("/register", response_model=UserResponse)
@limiter.limit("3/minute")
def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""

    email = user.email.strip()
    username = user.username.strip()
    password = user.password.strip()

    logger.info(f"Registration attempt for username: {username}, email: {email}")

    # Validate password strength
    is_valid, error_message = validate_password(password)
    if not is_valid:
        logger.warning(f"Registration failed - weak password for user: {username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    db_user = (db
               .query(User)
               .filter(
        User.username == username and
        User.email == email and
        User.is_verified == False
    ).first())

    if db_user:
        logger.info("There is a user with the same data, re-registering")
        try:
            db.delete(db_user)
            db.commit()
        except IntegrityError:
            traceback.print_exc()
            logger.info("User has data, treating as taken")
            raise HTTPException(
                status_code=400,
                detail="User is taken"
            )
    else:
        # Check if username already exists
        logger.debug(f"Checking if username exists: {username}")
        db_user = db.query(User).filter(User.username == username).first()
        if db_user:
            logger.warning(f"Registration failed - username already exists: {username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        logger.debug(f"Checking if email exists: {email}")
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            logger.warning(f"Registration failed - email already exists: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Create new user
    logger.debug(f"Creating new user: {username}")
    hashed_password = hash_password(password) # TODO #13: the password should already be hashed in the request
    # noinspection PyTypeChecker
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    try:
        send_verify_email(db_user, db)
    except Exception as e:
        logger.error("Email sending failed; this doesn't mean that the email wasn't delivered.")
        traceback.print_exc()

    logger.info(f"User registered successfully: {username} (ID: {db_user.id})")
    return db_user

@api_router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    logger.info(f"Login attempt for username: {user_credentials.username}")

    username = user_credentials.username.strip()
    password = user_credentials.password.strip()

    user = authenticate_user(db, username, password) # TODO #13: password should be hashed in the request

    if not user:
        logger.warning(f"Login failed for username: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_username = user.username.strip()

    if not user.is_verified:
        logger.warning(f"Login failed for unverified user: {user_username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"User authenticated, creating access token for: {user_username}")
    access_token = create_access_token(data={"sub": user_username})

    logger.info(f"Login successful for user: {user_username} (ID: {user.id})")
    return {"access_token": access_token}

@api_router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    blacklist_token(credentials.credentials)
    return {"message": "Logged out successfully"}

# Information
@api_router.get("/check-auth")
def check_auth_status(current_user: User = Depends(get_current_user)):
    return {"authenticated": True, "user": current_user.username}

@api_router.get("/user-info", response_model=UserResponse)
def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user