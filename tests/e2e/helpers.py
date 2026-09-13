from core import conf
from domain import Category


async def login_as_admin(page, username="andy", password="user1122"):
    """Вспомогательная функция для авторизации"""
    await page.goto(f"http://{conf.api_host}/admin")
    await page.get_by_label("Username").fill(username)
    await page.get_by_label("Password").fill(password)
    await page.get_by_role("button", name="Login").click()
