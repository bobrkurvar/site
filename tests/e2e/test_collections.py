import logging
from playwright.async_api import expect
from core import conf

from .helpers import login_as_admin

log = logging.getLogger(__name__)


async def test_admin_create_collection_success(page, image_files, category):
    main_img_path, _ = image_files
    target_collection = "Испанский Мрамор"
    await login_as_admin(page)
    await page.get_by_placeholder("Введите название коллекции").fill(target_collection)
    await page.locator("#collection_image").set_input_files(main_img_path)
    await page.locator("#category_id").select_option(label=category.name)
    await page.locator("#create-collection-btn").click()
    await page.wait_for_url("**/admin*")
    assert page.url == f"http://{conf.api_host}/admin"
    await expect(page).to_have_url(f"http://{conf.api_host}/admin")




async def test_admin_delete_collection_success(page, collection):
    await login_as_admin(page)
    await page.get_by_placeholder("Введите название коллекции").fill(collection.name)
    async def accept_dialog(dialog):
        await dialog.accept()
    page.once("dialog", accept_dialog)
    async with page.expect_response("**/admin"):
        await page.locator("#delete-collection-btn").click()
    await expect(page).to_have_url(f"http://{conf.api_host}/admin")
