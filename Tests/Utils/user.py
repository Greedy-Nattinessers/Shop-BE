import datetime
import imaplib
import os
import secrets

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email
from email.parser import BytesParser

from Services.Config.config import InvalidConfigError, config
from Services.Mail.mail import Purpose


def load_test_env(*args: str) -> dict[str, str]:
    load_dotenv()
    env = dict[str, str]()
    for arg in args:
        if (value := os.getenv(arg.upper())) is None:
            raise InvalidConfigError(f"Required environment variable {arg} not set")
        env[arg] = value
    return env


def get_captcha(
    server_url: str, server_port: int, email: str, password: str
) -> str | None:
    with imaplib.IMAP4_SSL(server_url, port=int(server_port)) as mail:
        mail.login(email, password)
        mail.select("inbox", readonly=True)
        _, data = mail.search(None, "FROM", config.email_addr)
        id = data[0].split()[-1]
        _, mail_data = mail.fetch(id, "(RFC822)")

        raw = BytesParser().parsebytes(mail_data[0][1])  # type: ignore
        for part in raw.walk():
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True).decode()  # type: ignore
                soup = BeautifulSoup(html_content, "html.parser")
                captcha = soup.find(id="captcha")
                return captcha.text.strip() if captcha else None
