from playwright.sync_api import expect
import logging
import re
from services.security import compute_user_fingerprint, get_hash
from services.auth import create_access_token, check_access_token

log = logging.getLogger(__name__)


def test_admin_login_success(page):
    page.goto("http://127.0.0.1:8000/admin")
    page.get_by_label("Username").fill("andy")
    page.get_by_label("Password").fill("user1122")
    with page.expect_request("**/admin/login/submit") as req_info:
        page.get_by_role("button", name="Login").click()
    request = req_info.value
    assert request.method == "POST"

    log.debug(page.url)
    expect(page).to_have_url(re.compile(r".*/admin"))


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
    access_token = create_access_token(data={"fp":fp})
    check_access_token(access_token, fp)
    custom_page.context.add_cookies([
        {
            "name": "access_token",
            "value": access_token,
            "domain": "127.0.0.1",
            "path": "/"
        }
    ])
    custom_page.goto("http://127.0.0.1:8000/admin")
    expect(custom_page).to_have_url(re.compile(r".*/admin"))
    context.close()


def test_admin_with_access_token_with_invalid_fingerprint(browser):
    user_agent = "agent"
    context = browser.new_context(user_agent=user_agent)
    wrong_user_agent = "wrong_agent"
    custom_page = context.new_page()
    fp = compute_user_fingerprint(wrong_user_agent, "127.0.0.1")
    fp = get_hash(fp)
    access_token = create_access_token(data={"fp":fp})
    check_access_token(access_token, fp)
    custom_page.context.add_cookies([
        {
            "name": "access_token",
            "value": access_token,
            "domain": "127.0.0.1",
            "path": "/"
        }
    ])
    custom_page.goto("http://127.0.0.1:8000/admin")
    expect(custom_page).to_have_url(re.compile(r".*/admin/submit"))
    context.close()