import logging
from pathlib import Path

import pytest
from services.tile import add_tile
from .helpers import product_catalog_path, product_details_path
from unittest.mock import AsyncMock

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_add_tile_creates_all_handbooks(
    products_env, tile, domain_handbooks_models_for_products
):
    repo = products_env.uow.db

    await add_tile(
        tile,
        products_env.image_generator,
        products_env.file_manager,
        products_env.uow,
    )

    assert domain_handbooks_models_for_products <= {type(obj) for obj in repo.created}


@pytest.mark.asyncio
async def test_add_tile_all_handbooks_already_exists(
    products_env, tile, domain_handbooks_models_for_products
):
    repo = products_env.uow.db
    repo.read_one = AsyncMock(return_value=object())

    await add_tile(
        tile,
        products_env.image_generator,
        products_env.file_manager,
        products_env.uow,
    )

    # Справочники не создавались, создалась только сама позиция tile
    assert len(repo.created) == 1
    assert repo.created[0] is tile


@pytest.mark.asyncio
async def test_expected_file_paths_exists_after_success_created(products_env, tile):
    env = products_env
    record = await add_tile(
        tile,
        env.image_generator,
        env.file_manager,
        env.uow,
    )
    paths_funcs = (
        env.file_manager.base_product_path,
        product_catalog_path(env.file_manager),
        product_details_path(env.file_manager),
    )
    assert len(env.fs) == 9
    for img in record.images:
        file_name = Path(img.image_path).name
        for func in paths_funcs:
            expected_path = Path(func(file_name)).as_posix()
            assert (
                expected_path in env.fs
            ), f"Файл не найден по ожидаемому пути: {expected_path}"
