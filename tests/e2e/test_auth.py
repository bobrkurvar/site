import logging
import re

from playwright.sync_api import expect

from core import conf

from .helpers import login_as_admin

log = logging.getLogger(__name__)


def test_admin_login_success(page):
    login_as_admin(page)
    log.debug(page.url)
    expect(page).to_have_url(re.compile(r".*/admin"))
    # на странице админа может высветиться html админки в случае успеха или
    # страница со вводом логина и пароля, которая содержит эти поля для ввода
    expect(page.get_by_label("Username")).to_have_count(0)
    expect(page.get_by_label("Password")).to_have_count(0)


def test_admin_login_user_not_found(page):
    login_as_admin(page, username="wrong_username")
    log.debug(page.url)
    expect(page).to_have_url(re.compile(r".*/admin/login/submit"))


def test_admin_refresh_access_token(page):
    # 1. Выполняем успешный логин
    login_as_admin(page)
    # Убеждаемся, что логин прошел успешно
    expect(page).to_have_url(re.compile(r".*/admin"))
    expect(page.get_by_label("Username")).to_have_count(0)

    # Удаляем access_token из cookies
    cookies = page.context.cookies()

    # В которой хранится токен доступа.
    filtered_cookies = [
        cookie for cookie in cookies if cookie["name"] != "access_token"
    ]

    # Очищаем все куки контекста и добавляем обратно все, кроме access_token
    page.context.clear_cookies()
    page.context.add_cookies(filtered_cookies)

    # Снова пытаемся зайти в админку (или просто обновляем страницу)
    page.goto(f"http://{conf.api_host}/admin")

    # Проверки успешного рефреша
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


def test_admin_refresh_token_reuse_compromised(page):
    # Выполняем успешный логин
    login_as_admin(page)
    expect(page).to_have_url(re.compile(r".*/admin"))

    # Крадем оригинальный refresh_token (Токен А)
    cookies = page.context.cookies()
    original_refresh_cookie = next(c for c in cookies if c["name"] == "refresh_token")

    # Провоцируем легальную ротацию (удаляем access_token)
    filtered_cookies = [c for c in cookies if c["name"] != "access_token"]
    page.context.clear_cookies()
    page.context.add_cookies(filtered_cookies)

    # Обновляем страницу, чтобы получить новые токены
    page.goto(f"http://{conf.api_host}/admin")
    expect(page).to_have_url(re.compile(r".*/admin"))  # Все еще внутри админки

    # Подменяем новый refresh_token обратно на старый (Токен А)
    # Сначала удаляем access_token, чтобы спровоцировать ротацию
    current_cookies = page.context.cookies()
    attack_cookies = [
        c for c in current_cookies if c["name"] not in ["access_token", "refresh_token"]
    ]
    # Возвращаем старый рефреш
    attack_cookies.append(original_refresh_cookie)

    page.context.clear_cookies()
    page.context.add_cookies(attack_cookies)

    # Пытаемся зайти с использованным рефрешем
    page.goto(f"http://{conf.api_host}/admin")

    # Проверяем последствия защиты
    # Нас должно было выкинуть на страницу логина
    expect(page.get_by_label("Username")).to_have_count(1)
    expect(page.get_by_label("Password")).to_have_count(1)

    # Опционально: убеждаемся, что сервер подчистил куки
    final_cookies = page.context.cookies()
    has_refresh = any(cookie["name"] == "refresh_token" for cookie in final_cookies)
    assert (
        has_refresh is False
    ), "Скомпрометированный refresh_token не был удален из cookies!"
