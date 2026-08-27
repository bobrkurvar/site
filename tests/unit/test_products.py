import logging
from pathlib import Path

import pytest
from tests.helpers import add_tile_helper
from .helpers import product_catalog_path, product_details_path

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_expected_file_paths_exists_after_success_created(products_env):
    env = products_env
    record = await add_tile_helper(
        uow=env.uow, file_manager=env.file_manager, images_generator=env.image_generator
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

