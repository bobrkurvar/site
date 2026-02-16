import logging
from decimal import Decimal

import pytest

import core.logger
from adapters.images import (ProductImagesManager,
                             generate_image_products_catalog_and_details)
from domain import (Categories, Producer, Tile, TileColor, TileImages,
                    TileSize, TileSurface)
from services.tile import add_tile, delete_tile, update_tile
from services.exceptions import ImageProcessingError
from tests.conftest import domain_handbooks_models

from .conftest import manager, manager_with_filled_handbooks
from .helpers import create_fake_image, product_files_count

log = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tile_success_when_handbooks_not_exists(
    domain_handbooks_models, manager_with_filled_handbooks
):
    file_manager = ProductImagesManager(root="tests/images")
    # выполнение add_tile
    record = await add_tile(
        name="Tile",
        length=Decimal(300),
        width=Decimal(200),
        height=Decimal(10),
        color_name="color",
        producer_name="producer",
        box_weight=Decimal(30),
        box_area=Decimal(1),
        boxes_count=3,
        main_image=create_fake_image(),
        category_name="category",
        manager=manager_with_filled_handbooks,
        images=[create_fake_image(), create_fake_image()],
        color_feature="feature",
        surface="surface",
        file_manager=file_manager,
        generate_images=generate_image_products_catalog_and_details,
    )

    # Tile создан
    assert record is not None
    tile_id = record["id"]

    # проверка всех справочников
    for model in domain_handbooks_models:
        handbook = await manager_with_filled_handbooks.read(model)
        assert len(handbook) == 1, f"model: {model}"

    images = await manager_with_filled_handbooks.read(TileImages, tile_id=tile_id)
    assert len(images) == 3
    assert product_files_count(file_manager) == 9


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tile_failure(domain_handbooks_models, manager):
    file_manager = ProductImagesManager(root="tests/images")

    async def generate_image_with_exc(*args, **kwargs):
        raise ImageProcessingError

    with pytest.raises(ImageProcessingError):
        await add_tile(
            name="Tile",
            length=Decimal(300),
            width=Decimal(200),
            height=Decimal(10),
            color_name="color",
            producer_name="producer",
            box_weight=Decimal(30),
            box_area=Decimal(1),
            boxes_count=3,
            main_image=create_fake_image(),
            category_name="category",
            manager=manager,
            images=[create_fake_image(), create_fake_image()],
            color_feature="feature",
            surface="surface",
            file_manager=file_manager,
            generate_images=generate_image_with_exc,
        )

    images = await manager.read(TileImages)
    assert len(images) == 0
    assert product_files_count(file_manager) == 0



@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_tile_success_when_new_attributes_in_handbooks(
    domain_handbooks_models, manager
):
    file_manager = ProductImagesManager(root="tests/images")

    # выполнение add_tile
    record = await add_tile(
        name="Tile",
        length=Decimal(300),
        width=Decimal(200),
        height=Decimal(10),
        color_name="color",
        producer_name="producer",
        box_weight=Decimal(30),
        box_area=Decimal(1),
        boxes_count=3,
        main_image=create_fake_image(),
        category_name="category",
        manager=manager,
        images=[create_fake_image(), create_fake_image()],
        color_feature="feature",
        surface="surface",
        file_manager=file_manager,
        generate_images=generate_image_products_catalog_and_details,
    )

    article = record["id"]  # фильтр для обновления по артикулу

    # новые данные
    new_filters = dict(
        name="NewTile",
        size={"length": Decimal(500), "width": Decimal(300), "height": Decimal(20)},
        color_name="NewColor",
        producer_name="NewProducer",
        box_weight=Decimal(50),
        box_area=Decimal(5),
        boxes_count=5,
        category_name="NewCategory",
        feature_name="NewFeature",
        surface_name="NewSurface",
    )

    await update_tile(manager, article, **new_filters)
    new_record = await manager.read(Tile, id=article, to_join=["box", "size"])

    # новый размер принимается на ввод как три числа через пробел, но для проверки данных и базы нужен их вид как чисел - длина, ширина, высота
    new_filters.pop("size")
    (
        new_filters["size_length"],
        new_filters["size_width"],
        new_filters["size_height"],
    ) = (Decimal(500), Decimal(300), Decimal(20))

    # проверка всех новых полей
    for f, v in new_filters.items():
        assert new_record[0][f] == v

    # Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    for model in domain_handbooks_models:
        rows = await manager.read(model)
        assert len(rows) == 2, f"{model} should have at least one row"


@pytest.mark.asyncio
async def test_delete_tile_by_article(manager_with_filled_handbooks):
    file_manager = ProductImagesManager(root="tests/images")

    record = await add_tile(
        name="Tile",
        length=Decimal(300),
        width=Decimal(200),
        height=Decimal(10),
        color_name="color",
        producer_name="producer",
        box_weight=Decimal(30),
        box_area=Decimal(1),
        boxes_count=3,
        main_image=create_fake_image(),
        category_name="category",
        manager=manager_with_filled_handbooks,
        images=[create_fake_image(), create_fake_image()],
        color_feature="feature",
        surface="surface",
        file_manager=file_manager,
        generate_images=generate_image_products_catalog_and_details,
    )

    article = record["id"]

    records = await delete_tile(
        manager_with_filled_handbooks, id=article, file_manager=file_manager
    )
    assert len(records) == 1

    for i in records:
        assert i["id"] == article

    new_records = await manager_with_filled_handbooks.read(Tile, id=article)
    assert not new_records

    # При удалении продукта записи в связанных справочника не должны удаляться
    should_be_handbooks = (TileSurface, TileColor, TileSize, Producer, Categories)
    for table_name in should_be_handbooks:
        rows = await manager_with_filled_handbooks.read(table_name)
        assert len(rows) == 1

    # изображение должно каскадно удалиться
    images = await manager_with_filled_handbooks.read(TileImages)
    assert len(images) == 0
    names = (f"{article}-0", f"{article}-1", f"{article}-2")
    # файлы изображений удалились
    assert product_files_count(file_manager) == 0
