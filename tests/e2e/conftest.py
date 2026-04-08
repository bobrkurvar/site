from playwright.sync_api import sync_playwright

import subprocess
import time
import pytest
import requests
import logging
from core.logger import setup_logging
from domain import Admin
from services.security import get_hash
from core import conf

setup_logging()
log = logging.getLogger(__name__)


# @pytest.fixture(scope="session", autouse=True)
# def site_api():
#     # Запуск Uvicorn в subprocess
#     process = subprocess.Popen(
#         ["uvicorn", "main_app:app", "--host", "127.0.0.1", "--port", "8000"],
#     )
#     for _ in range(5):
#         try:
#             r = requests.get("http://127.0.0.1:8000/health")
#             if r.status_code == 200:
#                 break
#         except requests.ConnectionError:
#             time.sleep(0.1)
#     else:
#         process.terminate()
#         raise RuntimeError("Не удалось поднять API для тестов")
#
#     yield
#
#     process.terminate()
#     process.wait()


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


# from sqlalchemy import text
#
# from infrastructure.crud import get_db_manager

#
# @pytest.fixture(scope="session")
# async def crud(request):
#     manager = get_db_manager(test=True)
#     manager.connect()
#     yield manager
#     engine = manager._engine
#     async with engine.begin() as conn:
#         await conn.execute(
#             text(
#                 """
#                 TRUNCATE
#                 admins
#
#                 RESTART IDENTITY CASCADE;
#                  """
#             )
#         )
#     await manager.close_and_dispose()
#
#
# @pytest.fixture(scope="session", autouse=True)
# async def add_admins(crud):
#     initial_admins = conf.initial_admins_list
#     for admin in initial_admins:
#         # log.debug("ADMIN: %s", admin)
#         password = get_hash(admin["password"])
#         # log.debug("HASH PASWORD: %s,", password)
#         await crud.create(Admin, username=admin["username"], password=password)
