from playwright.sync_api import sync_playwright, expect
import logging
import re

log = logging.getLogger(__name__)

def test_admin_login_success():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000/admin")
        page.get_by_label("Username").fill("andy")
        page.get_by_label("Password").fill("user1122")
        with page.expect_request("**/admin/login/submit") as req_info:
            page.get_by_role("button", name="Login").click()
        request = req_info.value
        assert request.method == "POST"

        log.debug(page.url)
        expect(page).to_have_url(re.compile(r".*/admin"))
        browser.close()


def test_admin_login_user_not_found():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000/admin")
        page.get_by_label("Username").fill("invalid_username")
        page.get_by_label("Password").fill("invalid_password")
        page.get_by_role("button", name="Login").click()
        log.debug(page.url)
        expect(page).to_have_url(re.compile(r".*/admin/login/submit"))
        browser.close()


def test_admin_login_wrong_password():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000/admin")
        page.get_by_label("Username").fill("andy")
        page.get_by_label("Password").fill("invalid_password")
        page.get_by_role("button", name="Login").click()
        log.debug(page.url)
        expect(page).to_have_url(re.compile(r".*/admin/login/submit"))
        browser.close()