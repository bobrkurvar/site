from playwright.sync_api import expect
import logging
import re
from services.security import compute_user_fingerprint, get_hash
from services.auth import create_access_token, create_refresh_token

log = logging.getLogger(__name__)


def test_admin_login_success(page):
    page.goto("http://127.0.0.1:8000/admin")
    page.get_by_label("Username").fill("andy")
    page.get_by_label("Password").fill("user1122")
    with page.expect_request("**/admin/login/submit") as req_info:
        page.get_by_role("button", name="Login").click()
    log.debug(page.url)
    expect(page).to_have_url(re.compile(r".*/admin"))
    # на странице админа может высветиться html админки в случае успеха или
    # страница со вводом логина и пароля, которая содержит эти поля для ввода
    expect(page.get_by_label("Username")).to_have_count(0)
    expect(page.get_by_label("Password")).to_have_count(0)

    cookies = page.context.cookies("http://127.0.0.1:8000")
    for cookie in cookies:
        if cookie["name"] == "access_token":
            log.debug(cookie["expires"])
            assert cookie["expires"] == 900


def test_admin_login_user_not_found(page):
    page.goto("http://127.0.0.1:8000/admin")
    page.get_by_label("Username").fill("invalid_username")
    page.get_by_label("Password").fill("invalid_password")
    page.get_by_role("button", name="Login").click()
    log.debug(page.url)
    expect(page).to_have_url(re.compile(r".*/admin/login/submit"))


def test_admin_login_wrong_password(page):
    page.goto("http://127.0.0.1:8000/admin")
    page.get_by_label("Username").fill("andy")
    page.get_by_label("Password").fill("invalid_password")
    page.get_by_role("button", name="Login").click()
    log.debug(page.url)
    expect(page).to_have_url(re.compile(r".*/admin/login/submit"))


def test_admin_with_access_token_with_valid_fingerprint(browser):
    user_agent = "agent"
    context = browser.new_context(user_agent=user_agent)
    custom_page = context.new_page()
    fp = compute_user_fingerprint(user_agent, "127.0.0.1")
    fp = get_hash(fp)
    access_token = create_access_token(data={"fp": fp})
    custom_page.context.add_cookies(
        [
            {
                "name": "access_token",
                "value": access_token,
                "domain": "127.0.0.1",
                "path": "/",
            }
        ]
    )
    custom_page.goto("http://127.0.0.1:8000/admin")
    expect(custom_page).to_have_url(re.compile(r".*/admin"))
    expect(custom_page.get_by_label("Username")).to_have_count(0)
    expect(custom_page.get_by_label("Password")).to_have_count(0)
    context.close()


def test_admin_with_access_token_with_invalid_fingerprint(browser):
    user_agent, wrong_user_agent = "agent", "wrong_agent"
    context = browser.new_context(user_agent=user_agent)
    custom_page = context.new_page()
    fp = compute_user_fingerprint(wrong_user_agent, "127.0.0.1")
    fp = get_hash(fp)
    access_token = create_access_token(data={"fp": fp})
    custom_page.context.add_cookies(
        [
            {
                "name": "access_token",
                "value": access_token,
                "domain": "127.0.0.1",
                "path": "/",
            }
        ]
    )
    custom_page.goto("http://127.0.0.1:8000/admin")
    expect(custom_page).to_have_url(re.compile(r".*/admin"))
    expect(custom_page.get_by_label("Username")).to_be_visible()
    expect(custom_page.get_by_label("Password")).to_be_visible()

    cookies = custom_page.context.cookies("http://127.0.0.1:8000")
    for cookie in cookies:
        if cookie["name"] in {"access_token", "refresh_token"}:
            assert not cookie["value"]
    context.close()


def test_admin_with_refresh_token_with_valid_fingerprint(browser):
    user_agent = "agent"
    context = browser.new_context(user_agent=user_agent)
    custom_page = context.new_page()
    fp = compute_user_fingerprint(user_agent, "127.0.0.1")
    fp = get_hash(fp)
    refresh_token = create_refresh_token(data={"fp": fp})
    custom_page.context.add_cookies(
        [
            {
                "name": "refresh_token",
                "value": refresh_token,
                "domain": "127.0.0.1",
                "path": "/admin",
            }
        ]
    )
    custom_page.goto("http://127.0.0.1:8000/admin")
    expect(custom_page).to_have_url(re.compile(r".*/admin"))
    expect(custom_page.get_by_label("Username")).to_have_count(0)
    expect(custom_page.get_by_label("Password")).to_have_count(0)
    context.close()


def test_admin_with_refresh_token_with_invalid_fingerprint(browser):
    user_agent, wrong_user_agent = "agent", "wrong_agent"
    context = browser.new_context(user_agent=user_agent)
    custom_page = context.new_page()
    fp = compute_user_fingerprint(wrong_user_agent, "127.0.0.1")
    fp = get_hash(fp)
    refresh_token = create_refresh_token(data={"fp": fp})
    custom_page.context.add_cookies(
        [
            {
                "name": "refresh_token",
                "value": refresh_token,
                "domain": "127.0.0.1",
                "path": "/admin",
            }
        ]
    )
    custom_page.goto("http://127.0.0.1:8000/admin")
    expect(custom_page).to_have_url(re.compile(r".*/admin"))
    expect(custom_page.get_by_label("Username")).to_be_visible()
    expect(custom_page.get_by_label("Password")).to_be_visible()

    cookies = custom_page.context.cookies("http://127.0.0.1:8000")
    for cookie in cookies:
        if cookie["name"] in {"access_token", "refresh_token"}:
            assert not cookie["value"]
    context.close()
