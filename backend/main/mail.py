import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import PathLike

import jinja2

from backend.main.constants import TEMPLATES_PATH

logger = logging.getLogger(__name__)

SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 465
SMTP_USER = "robot@toolbox-io.ru"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
if not SMTP_PASSWORD:
    raise RuntimeError("SMTP_PASSWORD environment variable not set")

def render_email(template_path: str, **kwargs) -> str:
    with open(
        TEMPLATES_PATH / "emails" / f"{template_path}.html", 
        encoding="utf-8"
    ) as template_file:
        template = jinja2.Template(template_file.read())
    return template.render(**kwargs)

def send_mail(to: str, subject: str, body: str, html: bool = False):
    if html:
        msg = MIMEMultipart("alternative")
    else:
        msg = MIMEText(body)
    
    msg["Subject"] = subject
    msg["From"] = "robot@toolbox-io.ru"
    msg["To"] = to

    if html:
        msg.attach(MIMEText(body, "html", "utf-8"))

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail("robot@toolbox-io.ru", [to], msg.as_string())