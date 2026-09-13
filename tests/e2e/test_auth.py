import logging
import re

from playwright.async_api import expect

from core import conf

from .helpers import login_as_admin

log = logging.getLogger(__name__)


async def test_admin_login_success(page):
    await login_as_admin(page)
    log.debug(page.url)
    await expect(page).to_have_url(re.compile(r".*/admin"))
    # на странице админа может высветиться html админки в случае успеха или
    # страница со вводом логина и пароля, которая содержит эти поля для ввода
    await expect(page.get_by_label("Username")).to_have_count(0)
    await expect(page.get_by_label("Password")).to_have_count(0)


async def test_admin_login_user_not_found(page):
    await login_as_admin(page, username="wrong_username")
    log.debug(page.url)
    await expect(page).to_have_url(re.compile(r".*/admin/login/submit"))


async def test_admin_refresh_access_token(page):
    # 1. Выполняем успешный логин
    await login_as_admin(page)
    # Убеждаемся, что логин прошел успешно
    await expect(page).to_have_url(re.compile(r".*/admin"))
    await expect(page.get_by_label("Username")).to_have_count(0)

    # Удаляем access_token из cookies
    cookies = await page.context.cookies()

    # В которой хранится токен доступа.
    filtered_cookies = [
        cookie for cookie in cookies if cookie["name"] != "access_token"
    ]

    # Очищаем все куки контекста и добавляем обратно все, кроме access_token
    await page.context.clear_cookies()
    await page.context.add_cookies(filtered_cookies)

    # Снова пытаемся зайти в админку (или просто обновляем страницу)
    await page.goto(f"http://{conf.api_host}/admin")

    # Проверки успешного рефреша
    log.debug(page.url)

    # Проверяем, что мы остались в админке, а не вылетели на страницу логина
    await expect(page).to_have_url(re.compile(r".*/admin"))

    # Проверяем, что форма логина не появилась
    await expect(page.get_by_label("Username")).to_have_count(0)
    await expect(page.get_by_label("Password")).to_have_count(0)

    # Приложение выдало новый access_token
    new_cookies = await page.context.cookies()
    has_access_token = any(cookie["name"] == "access_token" for cookie in new_cookies)
    assert (
        has_access_token is True
    ), "Access token не был обновлен и отсутствует в cookies"


async def test_admin_refresh_token_reuse_compromised(page):
    # Выполняем успешный логин
    await login_as_admin(page)
    await expect(page).to_have_url(re.compile(r".*/admin"))

    # Крадем оригинальный refresh_token (Токен А)
    cookies = await page.context.cookies()
    original_refresh_cookie = next(c for c in cookies if c["name"] == "refresh_token")

    # Провоцируем легальную ротацию (удаляем access_token)
    filtered_cookies = [c for c in cookies if c["name"] != "access_token"]
    await page.context.clear_cookies()
    await page.context.add_cookies(filtered_cookies)

    # Обновляем страницу, чтобы получить новые токены
    await page.goto(f"http://{conf.api_host}/admin")
    await expect(page).to_have_url(re.compile(r".*/admin"))  # Все еще внутри админки

    # Подменяем новый refresh_token обратно на старый (Токен А)
    # Сначала удаляем access_token, чтобы спровоцировать ротацию
    current_cookies = await page.context.cookies()
    attack_cookies = [
        c for c in current_cookies if c["name"] not in ["access_token", "refresh_token"]
    ]
    # Возвращаем старый рефреш
    attack_cookies.append(original_refresh_cookie)

    await page.context.clear_cookies()
    await page.context.add_cookies(attack_cookies)

    # Пытаемся зайти с использованным рефрешем
    await page.goto(f"http://{conf.api_host}/admin")

    # Проверяем последствия защиты
    # Нас должно было выкинуть на страницу логина
    await expect(page.get_by_label("Username")).to_have_count(1)
    await expect(page.get_by_label("Password")).to_have_count(1)

    # Опционально: убеждаемся, что сервер подчистил куки
    final_cookies = await page.context.cookies()
    has_refresh = any(cookie["name"] == "refresh_token" for cookie in final_cookies)
    assert (
        has_refresh is False
    ), "Скомпрометированный refresh_token не был удален из cookies!"
