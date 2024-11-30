import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

from Services.Config.config import config


class Purpose(Enum):
    REGISTER = "账户注册"
    RESET_PASSWORD = "密码找回"


secure_rng = secrets.SystemRandom()


with open("Templates/captcha.html", "r", encoding="utf-8") as f:
    captcha_template = f.read()


def _send_email(addr: str, subject: str, body: str):
    smtp = smtplib.SMTP_SSL(config.email_host, port=int(config.email_port), timeout=5)
    smtp.login(config.email_addr, config.email_pwd)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.email_addr
    msg["To"] = addr
    msg.attach(MIMEText(body, "html"))
    smtp.sendmail(config.email_addr, addr, msg.as_string())
    smtp.quit()


def send_captcha(addr: str, purpose: Purpose, ip: str) -> str:
    captcha = str(secure_rng.randrange(10000, 99999))
    body = captcha_template.format(captcha=captcha, purpose=purpose.value, ip=ip)
    _send_email(addr, purpose.value, body)
    return captcha
