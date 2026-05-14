from playwright.sync_api import expect
import logging
import re
from core import conf

log = logging.getLogger(__name__)


def test_admin_login_success(page):
    page.goto(f"http://{conf.api_host}/admin")
    page.get_by_label("Username").fill("andy")
    page.get_by_label("Password").fill("user1122")
    with page.expect_request("**/admin/login/submit"):
        page.get_by_role("button", name="Login").click()
    log.debug(page.url)
    expect(page).to_have_url(re.compile(r".*/admin"))
    # на странице админа может высветиться html админки в случае успеха или
    # страница со вводом логина и пароля, которая содержит эти поля для ввода
    expect(page.get_by_label("Username")).to_have_count(0)
    expect(page.get_by_label("Password")).to_have_count(0)


def test_admin_login_user_not_found(page):
    page.goto(f"http://{conf.api_host}/admin")
    page.get_by_label("Username").fill("invalid_username")
    page.get_by_label("Password").fill("invalid_password")
    page.get_by_role("button", name="Login").click()
    log.debug(page.url)
    expect(page).to_have_url(re.compile(r".*/admin/login/submit"))


def test_admin_login_wrong_password(page):
    page.goto(f"http://{conf.api_host}/admin")
    page.get_by_label("Username").fill("andy")
    page.get_by_label("Password").fill("invalid_password")
    page.get_by_role("button", name="Login").click()
    log.debug(page.url)
    expect(page).to_have_url(re.compile(r".*/admin/login/submit"))


def test_admin_refresh_access_token(page):
    # 1. Выполняем успешный логин
    page.goto(f"http://{conf.api_host}/admin")
    page.get_by_label("Username").fill("andy")
    page.get_by_label("Password").fill("user1122")
    with page.expect_request("**/admin/login/submit"):
        page.get_by_role("button", name="Login").click()

    # Убеждаемся, что логин прошел успешно
    expect(page).to_have_url(re.compile(r".*/admin"))
    expect(page.get_by_label("Username")).to_have_count(0)

    # 2. Удаляем access_token из cookies
    cookies = page.context.cookies()

    # ВНИМАНИЕ: Замените "access_token" на реальное название вашей куки,
    # в которой хранится токен доступа.
    filtered_cookies = [
        cookie for cookie in cookies if cookie["name"] != "access_token"
    ]

    # Очищаем все куки контекста и добавляем обратно все, кроме access_token
    page.context.clear_cookies()
    page.context.add_cookies(filtered_cookies)

    # 3. Снова пытаемся зайти в админку (или просто обновляем страницу)
    page.goto(f"http://{conf.api_host}/admin")

    # 4. Проверки успешного рефреша
    log.debug(page.url)

    # Проверяем, что мы остались в админке, а не вылетели на страницу логина
    expect(page).to_have_url(re.compile(r".*/admin"))

    # Проверяем, что форма логина не появилась
    expect(page.get_by_label("Username")).to_have_count(0)
    expect(page.get_by_label("Password")).to_have_count(0)

    # Приложение выдало новый access_token
    new_cookies = page.context.cookies()
    has_access_token = any(cookie["name"] == "access_token" for cookie in new_cookies)
    assert (
        has_access_token is True
    ), "Access token не был обновлен и отсутствует в cookies"
