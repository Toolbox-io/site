import datetime
import logging
import random

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants import CONTENT_PATH
from db.core import get_db, get_session_factory
from limiter import limiter
from models import PasswordChange, Message, User
from routes.auth.utils import hash_password, get_current_user, verify_password, validate_password, send_verify_email
from mail import render_email, send_mail

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/change-password", response_model=Message)
@limiter.limit("1/minute")
def change_password(
    request: Request,
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    logger.info(f"Password change attempt for user: {current_user.username} (ID: {current_user.id})")

    try:
        # Verify current password
        logger.debug(f"Verifying current password for user: {current_user.username}")
        if not verify_password(password_change.current_password, current_user.hashed_password):
            logger.warning(f"Password change failed - incorrect current password for user: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Hash new password and update
        logger.debug(f"Hashing new password for user: {current_user.username}")
        new_hashed_password = hash_password(password_change.new_password)
        current_user.hashed_password = new_hashed_password
        db.commit()

        logger.info(f"Password changed successfully for user: {current_user.username}")
        return {"message": "Password changed successfully"}

    except HTTPException:
        raise

@router.delete("/delete-account")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    logger.info(f"Account deletion request for user: {current_user.username}")

    try:
        db.delete(current_user)
        db.commit()
        logger.info(f"Account deleted successfully for user: {current_user.username}")
        return {"message": "Account deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete account: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete account"
        )

def verify_email_code(code: str) -> bool:
    db = get_session_factory()()
    user = db.query(User).filter(User.verification_code == code).first()
    if not user:
        return False
    user.is_verified = True
    user.verification_code = None
    db.commit()

    return True

@router.get("/verify")
@router.post("/verify")
@limiter.limit("1/minute")
async def verify_email(request: Request, code: str):
    if not verify_email_code(code):
        raise HTTPException(status_code=404, detail="Invalid or expired code")
    if request.method == "POST":
        return {"success": True}
    else:
        return RedirectResponse(url="/account/login?verified=true")

@router.post("/request-reset")
@limiter.limit("1/minute")
async def request_reset(request: Request, data: dict = Body(...)):
    email = data.get("email")
    if not isinstance(email, str):
        raise HTTPException(status_code=400, detail="Invalid email format")
    db = get_session_factory()()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"success": True}  # Don't reveal if email exists
    code = str(random.randint(1, 999999)).zfill(6)
    user.reset_code = code
    user.reset_token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
    db.commit()
    html_body = render_email("reset", CODE=code)
    send_mail(
        email,
        "Сброс пароля",
        html_body,
        html=True
    )
    return {"success": True}

@router.get("/check-reset")
def check_reset_code(
    data: dict = Body(...)
):
    db = get_session_factory()()
    code: str | None = data.get("code")
    user: User | None = db.query(User).filter(User.reset_code == code).first()
    if not user or user.reset_token_expiry < datetime.datetime.now():
        raise HTTPException(status_code=400, detail="Invalid code")
    return {"success": True}

@router.post("/reset-password")
@limiter.limit("1/minute")
async def reset_password(request: Request, data: dict = Body(...)):
    code: str | None = data.get("code")
    new_password: str | None = data.get("new_password")
    db = get_session_factory()()
    user: User | None = db.query(User).filter(User.reset_code == code).first()
    if not user or user.reset_token_expiry < datetime.datetime.now():
        logger.warning(f"Reset password failed for {code}")
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    valresult = validate_password(new_password)
    if not valresult[0]:
        logger.warning(f"Password is too weak. {code}")
        raise HTTPException(status_code=400, detail=valresult[1])
    user.hashed_password = hash_password(new_password)
    user.reset_code = None
    user.reset_token_expiry = None
    db.commit()
    return {"success": True}

@router.post("/verify-email")
@limiter.limit("1/minute")
async def verify_email_post(request: Request, data: dict = Body(...)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Missing email")
    db = get_session_factory()()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    send_verify_email(user, db)
    return {"success": True}