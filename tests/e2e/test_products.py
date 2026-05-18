import re
from playwright.sync_api import expect
from core import conf
import logging

log = logging.getLogger(__name__)

def login_as_admin(page):
    """Вспомогательная функция для авторизации"""
    page.goto(f"http://{conf.api_host}/admin")
    page.get_by_label("Username").fill("andy")
    page.get_by_label("Password").fill("user1122")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(re.compile(r".*/admin"))


def create_tile_ui_helper(page, tile_name, dummy_images):
    main_img_path, add_img_path = dummy_images

    page.get_by_placeholder("Название товара").fill(tile_name)
    page.locator("#main_image").set_input_files(main_img_path)
    page.locator("#images").set_input_files([add_img_path])
    page.get_by_placeholder("Тип товара").fill("Керамогранит")
    page.get_by_placeholder("Размер товара").fill("60 60 10")
    page.get_by_placeholder("Название цвета").fill("Белый")
    page.get_by_placeholder("Свойство цвета").fill("Глянцевый")
    page.get_by_placeholder("Название поверхности").fill("Полированная")
    page.get_by_placeholder("Выберите производителя").fill("Kerama Marazzi")
    page.get_by_placeholder("Вес коробки").fill("25.5")
    page.get_by_placeholder("Метры").fill("1.44")
    page.get_by_placeholder("Количество коробок").fill("50")

    with page.expect_response("**/admin/tiles/create") as response_info:
        page.locator("#add-btn").click()

    response = response_info.value
    if response.status == 422:
        log.debug("response: %s", response.json())

    expect(page).to_have_url(f"http://{conf.api_host}/admin")


def test_admin_create_tile_success(page, dummy_images):
    login_as_admin(page)
    target_name = "Мраморный узор"
    create_tile_ui_helper(page, target_name, dummy_images)
    expect(page.get_by_text(target_name)).to_be_visible()


def test_admin_delete_tile_success(page, dummy_images):
    login_as_admin(page)
    target_name = "Плитка для удаления"
    create_tile_ui_helper(page, target_name, dummy_images)
    expect(page.get_by_text(target_name)).to_be_visible()

    tile_item = page.locator(".tile-item", has_text=target_name)


    with page.expect_request("**/admin/tiles/delete"):
        tile_item.get_by_role("button", name="Удалить").click()

    expect(page).to_have_url(f"http://{conf.api_host}/admin")
    expect(page.get_by_text(target_name)).to_have_count(0)