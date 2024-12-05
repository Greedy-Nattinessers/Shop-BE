import datetime
import secrets
from time import sleep

from fastapi.testclient import TestClient

from main import app
from Services.Mail.mail import Purpose
from Tests.Utils.user import get_captcha, load_test_env

client = TestClient(app)


class TestUser:
    email: str
    username: str
    password: str
    created_at: datetime.datetime
    token: str | None

    def __init__(self, email: str):
        secure_rng = secrets.SystemRandom()
        self.email = email
        self.username = f"BotDuang-{secure_rng.randint(1000, 9999)}"
        self.password = secrets.token_urlsafe(16)
        self.created_at = datetime.datetime.now()


env = load_test_env(
    "test_email_host", "test_email_port", "test_email_addr", "test_email_pwd"
)
test_user = TestUser(env["test_email_addr"])


def test_user_register():
    captcha_response = client.get(
        "/user/captcha",
        params={"email": test_user.email, "purpose": Purpose.REGISTER.value},
    )

    assert captcha_response.status_code == 200
    assert captcha_response.json()["status_code"] == 200
    sleep(5)

    captcha = get_captcha(
        env["test_email_host"],
        int(env["test_email_port"]),
        env["test_email_addr"],
        env["test_email_pwd"],
    )

    assert isinstance(captcha, str)
    register_response = client.post(
        "/user/register",
        data={
            "email": test_user.email,
            "username": test_user.username,
            "password": test_user.password,
            "captcha": captcha,
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["status_code"] == 201

def test_user_login():
    login_response = client.post(
        "/user/login",
        data={"username": test_user.username, "password": test_user.password},
    )

    assert login_response.status_code == 200
    assert login_response.json()["data"]["access_token"] is not None
    test_user.token = login_response.json()["data"]["access_token"]

