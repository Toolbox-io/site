import datetime
import logging
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jinja2
from fastapi import APIRouter, Body, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from auth_api import hash_password, validate_password
from constants import CONTENT_PATH
from database import get_session_factory
from limiter import limiter
from models import User

logger = logging.getLogger(__name__)

# Path to the email templates
EMAIL_TEMPLATE_PATH = CONTENT_PATH / "emails" / "verify.html"
RESET_TEMPLATE_PATH = CONTENT_PATH / "emails" / "reset.html"

def render_verify_email_html(token: str) -> str:
    with open(EMAIL_TEMPLATE_PATH, encoding="utf-8") as f:
        template = jinja2.Template(f.read())
    return template.render(TOKEN=token)

def render_reset_email_html(token: str) -> str:
    with open(RESET_TEMPLATE_PATH, encoding="utf-8") as f:
        template = jinja2.Template(f.read())
    return template.render(TOKEN=token)

def send_mail(to: str, subject: str, body: str, html: bool = False):
    if html:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = "robot@toolbox-io.ru"
        msg["To"] = to
        part = MIMEText(body, "html", "utf-8")
        msg.attach(part)
    else:
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


# noinspection PyUnusedLocal
@router.get("/verify")
@limiter.limit("1/minute")
async def verify_email(request: Request, token: str):
    db = get_session_factory()()
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return RedirectResponse(url="/account/login?verified=true")


# noinspection PyUnusedLocal
@router.post("/request-reset")
@limiter.limit("1/minute")
async def request_reset(request: Request, data: dict = Body(...)):
    print(data)
    email = data.get("email")
    if not isinstance(email, str):
        raise HTTPException(status_code=400, detail="Invalid email format")
    db = get_session_factory()()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"success": True}  # Don't reveal if email exists
    token = str(uuid.uuid4())
    user.reset_token = token
    user.reset_token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
    db.commit()
    html_body = render_reset_email_html(token)
    send_mail(
        email,
        "Сброс пароля Toolbox.io",
        html_body,
        html=True
    )
    return {"success": True}

@router.get("/check-reset")
def check_reset_token(
    data: dict = Body(...)
):
    db = get_session_factory()()

    token: str | None = data.get("token")
    user: User | None = db.query(User).filter(User.reset_token == token).first()

    if not user or user.reset_token_expiry < datetime.datetime.now():
        raise HTTPException(status_code=400, detail="Invalid token")

    return {"success": True}

# noinspection PyUnusedLocal
@router.post("/reset-password")
@limiter.limit("1/minute")
async def reset_password(request: Request, data: dict = Body(...)):
    token: str | None = data.get("token")
    new_password: str | None = data.get("new_password")
    db = get_session_factory()()
    user: User | None = db.query(User).filter(User.reset_token == token).first()

    if not user or user.reset_token_expiry < datetime.datetime.now():
        logger.warning(f"Reset password failed for {token}")
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    valresult = validate_password(new_password)
    if not valresult[0]:
        logger.warning(f"Password is too weak. {token}")
        raise HTTPException(status_code=400, detail=valresult[1])

    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    return {"success": True}


# noinspection PyUnusedLocal
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
    verification_token = str(uuid.uuid4())
    user.verification_token = verification_token
    db.commit()
    html_body = render_verify_email_html(verification_token)
    send_mail(
        user.email,
        "Подтвертите ваш email",
        html_body,
        html=True
    )
    return {"success": True}