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


