import logging

from playwright.sync_api import expect

from core import conf

from .helpers import login_as_admin

log = logging.getLogger(__name__)


def test_admin_create_tile_success(page, dummy_images):
    login_as_admin(page)
    main_img_path, add_img_path = dummy_images

    page.get_by_placeholder("Название товара").fill("Мраморный узор")
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
    # expect(page.get_by_text(target_name)).to_be_visible()


def test_admin_delete_tile_success(page, dummy_images, add_tile):
    login_as_admin(page)
    target_name = "Плитка для удаления"
    add_tile(target_name)
    page.reload()
    tile_item = page.locator(".tile-item", has_text=target_name)
    page.once("dialog", lambda dialog: dialog.accept())

    with page.expect_response("**/admin/tiles/delete"):
        tile_item.get_by_role("button", name="Удалить").click()

    expect(page).to_have_url(f"http://{conf.api_host}/admin")
    expect(page.locator(".tile-list").get_by_text(target_name)).to_have_count(0)


def test_admin_update_tile_max_parameters_success(page, dummy_images, add_tile):
    login_as_admin(page)
    initial_name = "Плитка для апдейта"
    updated_name = "Обновленный Люкс Гранит"
    tile = add_tile(initial_name)
    # page.reload()
    page.locator("#article").fill(str(tile.article))
    page.get_by_placeholder("Название товара").fill(updated_name)
    page.get_by_placeholder("Тип товара").fill("Клинкер")
    page.get_by_placeholder("Размер товара").fill("80 80 11")
    page.get_by_placeholder("Название цвета").fill("Черный")
    page.get_by_placeholder("Свойство цвета").fill("Матовый")
    page.get_by_placeholder("Название поверхности").fill("Лаппатированная")
    page.get_by_placeholder("Выберите производителя").fill("Italon")
    page.get_by_placeholder("Вес коробки").fill("30.2")
    page.get_by_placeholder("Метры").fill("1.6")
    page.get_by_placeholder("Количество коробок").fill("120")

    # Жмем кнопку "Обновить", отправляя форму на **/admin/tiles/create или куда ведет экшен формы
    # (В твоем HTML у формы нет action, значит она шлет саму на себя POST-запросом)
    with page.expect_response("**/admin**") as response_info:
        page.locator("#update-btn").click()

    expect(page).to_have_url(f"http://{conf.api_host}/admin")

    # Проверяем, что старое имя исчезло, а новое появилось в списке
    expect(page.locator(".tile-list").get_by_text(updated_name)).to_be_visible()
    expect(page.locator(".tile-list").get_by_text(initial_name)).to_have_count(0)
