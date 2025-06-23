import smtplib
from email.mime.text import MIMEText

from fastapi import APIRouter, Body

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