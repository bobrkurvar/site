from core import conf
from domain import Category


def login_as_admin(page, username="andy", password="user1122"):
    """Вспомогательная функция для авторизации"""
    page.goto(f"http://{conf.api_host}/admin")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login").click()
