import smtplib
from email.mime.text import MIMEText

from fastapi import APIRouter, Body, HTTPException
import uuid
import datetime
from database import get_session_factory
from passlib.hash import bcrypt
from models import User

from utils import debug_only


def send_mail(to: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "robot@toolbox-io.ru"
    msg["To"] = to

    # Change these as needed for your SMTP server
    smtp_server = "smtp.mail.ru"
    smtp_port = 465
    smtp_user = "robot@toolbox-io.ru"
    smtp_password = "UGwUOEI2VMWZ1hZ8mqlF"

    with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail("robot@toolbox-io.ru", [to], msg.as_string())

router = APIRouter()

@router.post("/send/test")
@debug_only
async def send_test_email(data: dict = Body(...)):
    target_email = data.get("email")
    if not target_email:
        return {"error": "Missing email in request body"}
    try:
        send_mail(target_email, "Test Email", "test")
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

@router.get("/verify")
async def verify_email(token: str):
    db = get_session_factory()()
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"success": True, "message": "Email verified!"}

@router.post("/request-reset")
async def request_reset(data: dict = Body(...)):
    email = data.get("email")
    db = get_session_factory()()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"success": True}  # Don't reveal if email exists
    token = str(uuid.uuid4())
    user.reset_token = token
    user.reset_token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
    db.commit()
    send_mail(email, "Password Reset", f"Click to reset: https://beta.toolbox-io.ru/reset-password?token={token}")
    return {"success": True}

@router.post("/reset-password")
async def reset_password(data: dict = Body(...)):
    token = data.get("token")
    new_password = data.get("new_password")
    db = get_session_factory()()
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or user.reset_token_expiry < datetime.datetime.now():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.hashed_password = bcrypt.hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    return {"success": True}

@router.post("/verify-email")
async def verify_email_post(data: dict = Body(...)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Missing email")
    db = get_session_factory()()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    verification_token = str(uuid.uuid4())
    user.verification_token = verification_token
    db.commit()
    send_mail(user.email, "Verify your email", f"Click to verify: https://beta.toolbox-io.ru/verify?token={verification_token}")
    return {"success": True}