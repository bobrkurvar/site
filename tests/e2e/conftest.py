from playwright.sync_api import sync_playwright
import pytest
import logging
from core.logger import setup_logging

setup_logging()
log = logging.getLogger(__name__)



@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


