import logging

from playwright.sync_api import expect

from core import conf

from .helpers import login_as_admin

log = logging.getLogger(__name__)


def test_admin_create_collection_success(page, dummy_images, add_categories):
    main_img_path, _ = dummy_images
    target_collection, category_name = "Испанский Мрамор", "Керамогранит"
    add_categories(category_name)
    login_as_admin(page)
    page.get_by_placeholder("Введите название коллекции").fill(target_collection)
    page.locator("#collection_image").set_input_files(main_img_path)
    page.locator("#category_name").select_option(label=category_name)
    with page.expect_response("**/admin"):
        page.locator("#create-collection-btn").click()
    expect(page).to_have_url(f"http://{conf.api_host}/admin")


def test_admin_create_category_for_collection_success(
    page, dummy_images, add_collection
):
    target_name, category_name = "Испанский Мрамор", "Керамогранит"
    add_collection(target_name, category_name)
    login_as_admin(page)
    page.get_by_placeholder("Введите название коллекции").fill(target_name)
    page.locator("#category_name").select_option(label=category_name)
    with page.expect_response("**/admin"):
        page.locator("#create-collection-btn").click()
    expect(page).to_have_url(f"http://{conf.api_host}/admin")


def test_admin_delete_collection_success(page, dummy_images, add_collection):
    target_name = "Коллекция для удаления"
    add_collection(target_name)
    login_as_admin(page)
    page.get_by_placeholder("Введите название коллекции").fill(target_name)
    page.once("dialog", lambda dialog: dialog.accept())
    with page.expect_response("**/admin"):
        page.locator("#delete-collection-btn").click()
    expect(page).to_have_url(f"http://{conf.api_host}/admin")
