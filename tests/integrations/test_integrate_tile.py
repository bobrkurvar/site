import logging
from decimal import Decimal

import pytest

import core.logger
from domain import (Box, Categories, Producer, Tile, TileColor, TileImages,
                    TileSize, TileSurface)
from services.tile import add_tile, delete_tile, update_tile

from tests.fakes import generate_products_images
from adapters.crud import get_db_manager
from adapters.images import ProductImagesManager
from .helpers import product_files_count

log = logging.getLogger(__name__)

@pytest.mark.asyncio
@pytest.mark.integration
async def test_integrate_create_tile_success_when_all_handbooks_exists():
    manager = get_db_manager(test=True)
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
        main_image=b"MAIN",
        category_name="category",
        manager=manager,
        images=[b"A", b"B"],
        color_feature="feature",
        surface="surface",
        file_manager=file_manager,
        generate_images=generate_products_images
    )

    # 1. Tile создан
    assert record is not None
    assert "id" in record
    tile_id = record["id"]

    images = await manager.read(TileImages, tile_id=tile_id)
    assert len(images) == 3
    names = {f"{tile_id}-{i}" for i in range(3)}
    log.debug("names: %s", names)
    assert product_files_count(file_manager) == 9


# @pytest.mark.asyncio
# async def test_create_tile_success_when_all_handbooks_not_exists(
#     manager_without_handbooks
# ):
#     manager = manager_without_handbooks
#     fs = {}
#
#     # выполнение add_tile
#     record = await add_tile(
#         name="Tile",
#         length=Decimal(300),
#         width=Decimal(200),
#         height=Decimal(10),
#         color_name="color",
#         producer_name="producer",
#         box_weight=Decimal(30),
#         box_area=Decimal(1),
#         boxes_count=3,
#         main_image=b"MAIN",
#         category_name="category",
#         manager=manager,
#         images=[b"A", b"B"],
#         color_feature="feature",
#         surface="surface",
#         uow_class=FakeUoW,  # поддельная транзакция
#         save_files=get_fake_save_files_function_with_fs(fs),
#         generate_image_variant_callback=noop
#     )
#
#     # 1. Tile создан
#     assert record is not None
#     assert "id" in record
#
#
#     # 2. Проверка всех справочников
#     tables = (Box, Categories, Producer, Tile, TileColor, TileImages, TileSize, TileSurface)
#
#     for table_name in tables:
#         rows = await manager.read(table_name)
#         assert rows, f"{table_name.__name__} should have at least one row"
#
#     # 3. Все изображения записались во фейковую ФС
#     tile_id = record["id"]
#     expected_paths = [
#         str(Path(f"static/images/base/products/{tile_id}-0")),
#         str(Path(f"static/images/base/products/{tile_id}-1")),
#         str(Path(f"static/images/base/products/{tile_id}-2")),
#     ]
#
#     assert set(fs) == set(expected_paths)
#
#     assert fs[expected_paths[0]] == b"MAIN"
#     assert fs[expected_paths[1]] == b"A"
#     assert fs[expected_paths[2]] == b"B"
#
#     images_table = await manager.read(TileImages)
#
#     assert len(images_table) == 3
#     stored_paths = [row["image_path"] for row in images_table]
#     assert stored_paths == expected_paths

#
# @pytest.mark.asyncio
# async def test_update_tile_success_when_new_attributes_in_handbooks(
#     manager_with_handbooks
# ):
#     manager = manager_with_handbooks
#
#     record = await add_tile(
#         name="Tile",
#         length=Decimal(300),
#         width=Decimal(200),
#         height=Decimal(10),
#         color_name="color",
#         producer_name="producer",
#         box_weight=Decimal(30),
#         box_area=Decimal(1),
#         boxes_count=3,
#         main_image=b"MAIN",
#         category_name="category",
#         manager=manager,
#         images=[b"A", b"B"],
#         color_feature="feature",
#         surface="surface",
#         uow_class=FakeUoW,
#         save_files=noop,
#         generate_image_variant_callback=noop
#     )
#     article = record["id"] # фильтр для обновления по артикулу
#
#     # новые данные
#     new_filters = dict(
#         name="NewTile",
#         size="500 300 20",
#         color_name="NewColor",
#         producer_name="NewProducer",
#         box_weight=Decimal(50),
#         box_area=Decimal(5),
#         boxes_count=5,
#         category_name="NewCategory",
#         feature_name="NewFeature",
#         surface_name="NewSurface",
#     )
#
#     await update_tile(manager, article, uow_class=FakeUoW, **new_filters)
#     new_record = await manager.read(Tile, id=article, to_join=["box", "size"])
#
#     # новый размер принимается на ввод как три числа через пробел, но для проверки данных и базы нужен их вид как чисел - длина, ширина, высота
#     new_filters.pop("size")
#     (
#         new_filters["size_length"],
#         new_filters["size_width"],
#         new_filters["size_height"],
#     ) = (Decimal(500), Decimal(300), Decimal(20))
#
#     # 1 проверка всех новых полей
#     for f, v in new_filters.items():
#         assert new_record[0][f] == v
#
#     # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
#     should_new_handbooks = [
#         table
#         for table in manager.storage.tables
#         if table is not Tile and table is not TileImages
#     ]
#     for table_name in should_new_handbooks:
#         rows = await manager.read(table_name)
#         assert len(rows) == 2, f"{table_name.__name__} should have at least one row"
#
#
# @pytest.mark.asyncio
# async def test_delete_tile_by_article(
#     manager_with_handbooks
# ):
#     manager = manager_with_handbooks
#     fs = {}
#
#     record = await add_tile(
#         name="Tile",
#         length=Decimal(300),
#         width=Decimal(200),
#         height=Decimal(10),
#         color_name="color",
#         producer_name="producer",
#         box_weight=Decimal(30),
#         box_area=Decimal(1),
#         boxes_count=3,
#         main_image=b"MAIN",
#         category_name="category",
#         manager=manager,
#         images=[b"A", b"B"],
#         color_feature="feature",
#         surface="surface",
#         uow_class=FakeUoW,
#         save_files=get_fake_save_files_function_with_fs(fs),
#         generate_image_variant_callback=get_fake_save_bg_products_and_details_with_fs(fs)
#     )
#
#     article = record["id"]
#     expected_paths = [
#         f"static/images/base/products/{article}-0",
#         f"static/images/base/products/{article}-1",
#         f"static/images/base/products/{article}-2",
#     ]
#     log.debug("FS: %s", fs)
#
#     records = await delete_tile(manager, uow_class=FakeUoW, id=article, delete_files=get_fake_delete_files_function_with_fs(fs))
#     assert len(records) == 1
#
#     for path in expected_paths:
#         assert path not in fs.keys()
#
#     for i in records:
#         assert i['id'] == article
#
#     new_records = await manager.read(Tile, id=article)
#     assert new_records == []
#
#     should_be_handbooks = [
#         table
#         for table in manager.storage.tables
#         if table is not Tile and table is not TileImages
#     ]
#     for table_name in should_be_handbooks:
#         rows = await manager.read(table_name)
#         assert len(rows) == 1
#
#
