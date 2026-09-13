import logging

from playwright.async_api import expect

from core import conf

from .helpers import login_as_admin

log = logging.getLogger(__name__)


async def test_admin_create_tile_success(page, image_files):
    await login_as_admin(page)
    main_img_path, add_img_path = image_files

    await page.get_by_placeholder("Название товара").fill("Мраморный узор")
    await page.locator("#main_image").set_input_files(main_img_path)
    await page.locator("#images").set_input_files([add_img_path])
    await page.get_by_placeholder("Тип товара").fill("Керамогранит")
    await page.get_by_placeholder("Размер товара").fill("60 60 10")
    await page.get_by_placeholder("Название цвета").fill("Белый")
    await page.get_by_placeholder("Свойство цвета").fill("Глянцевый")
    await page.get_by_placeholder("Название поверхности").fill("Полированная")
    await page.get_by_placeholder("Выберите производителя").fill("Kerama Marazzi")
    await page.get_by_placeholder("Вес коробки").fill("25.5")
    await page.get_by_placeholder("Метры").fill("1.44")
    await page.get_by_placeholder("Количество коробок").fill("50")

    async with page.expect_response("**/admin/tiles/create") as response_info:
        await page.locator("#add-btn").click()

    response = await response_info.value
    if response.status == 422:
        log.debug("response: %s", response.json())
    await expect(page).to_have_url(f"http://{conf.api_host}/admin")


async def test_admin_delete_tile_success(page, created_tile):
    await login_as_admin(page)
    await page.get_by_text("Список товаров", exact=False).click()

    tile_item = page.locator(".tile-item", has_text=created_tile.name)

    async def accept_dialog(dialog):
        await dialog.accept()
    page.once("dialog", accept_dialog)

    async with page.expect_response("**/admin/tiles/delete"):
        await tile_item.get_by_role(
            "button",
            name="Удалить",
        ).click()

    await expect(page).to_have_url(f"http://{conf.api_host}/admin")

    await expect(
        page.locator(".tile-list").get_by_text(
            created_tile.name,
            exact=True,
        )
    ).to_have_count(0)


async def test_admin_update_tile_max_parameters_success(page, created_tile):
    await login_as_admin(page)
    initial_name, updated_name = created_tile.name, f"обновлённый {created_tile.name}"
    # page.reload()
    await page.locator("#article").fill(str(created_tile.article))
    await page.get_by_placeholder("Название товара").fill(updated_name)
    await page.get_by_placeholder("Тип товара").fill("Клинкер")
    await page.get_by_placeholder("Размер товара").fill("80 80 11")
    await page.get_by_placeholder("Название цвета").fill("Черный")
    await page.get_by_placeholder("Свойство цвета").fill("Матовый")
    await page.get_by_placeholder("Название поверхности").fill("Лаппатированная")
    await page.get_by_placeholder("Выберите производителя").fill("Italon")
    await page.get_by_placeholder("Вес коробки").fill("30.2")
    await page.get_by_placeholder("Метры").fill("1.6")
    await page.get_by_placeholder("Количество коробок").fill("120")

    # Жмем кнопку "Обновить", отправляя форму на **/admin/tiles/create или куда ведет экшен формы
    # (В твоем HTML у формы нет action, значит она шлет саму на себя POST-запросом)
    async with page.expect_response("**/admin**") as response_info:
        await page.locator("#update-btn").click()

    await expect(page).to_have_url(f"http://{conf.api_host}/admin")

    # Проверяем, что старое имя исчезло, а новое появилось в списке
    await expect(page.locator(".tile-list").get_by_text(updated_name, exact=True)).to_have_count(1)
    await expect(page.locator(".tile-list").get_by_text(initial_name, exact=True)).to_have_count(0)
