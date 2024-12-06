import imaplib
from email.parser import BytesParser

from bs4 import BeautifulSoup

from Services.Config.config import InvalidConfigError, config


def get_captcha(
    host: str, port: int, address: str, password: str
) -> str | None:
    if config.test is None:
        raise InvalidConfigError("Test environment not enabled")

    with imaplib.IMAP4_SSL(host, port=int(port)) as mail:
        mail.login(address, password)
        mail.select("inbox", readonly=True)
        _, data = mail.search(None, "FROM", config.test.email.address)
        id = data[0].split()[-1]
        _, mail_data = mail.fetch(id, "(RFC822)")

        raw = BytesParser().parsebytes(mail_data[0][1])  # type: ignore
        for part in raw.walk():
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True).decode()  # type: ignore
                soup = BeautifulSoup(html_content, "html.parser")
                captcha = soup.find(id="captcha")
                return captcha.text.strip() if captcha else None
