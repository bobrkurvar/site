import logging
import shutil
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from adapters.crud import get_db_manager
from core import conf
from domain import Categories

log = logging.getLogger(__name__)



@pytest.fixture
async def manager(request):
    manager = get_db_manager(test=True)
    manager.connect()
    yield manager
    engine = manager._engine
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
            TRUNCATE
                tile_images,
                categories,
                producers,
                tile_sizes,
                boxes,
                catalog,
                tile_colors,
                collections,
                tile_surface,
                slugs,
                collection_category
                
            RESTART IDENTITY CASCADE;
        """
            )
        )
    await manager.close_and_dispose()


@pytest.fixture
async def manager_with_categories(manager):
    category_name1, category_name2 = "category1", "category2"
    await manager.create(Categories, name=category_name1)
    await manager.create(Categories, name=category_name2)
    return manager


@pytest.fixture(autouse=True)
def clean_fs_after_test(request):
    yield
    images_path = Path("tests/images")
    if images_path.exists() and images_path.is_dir():
        shutil.rmtree(images_path)


@pytest.fixture(scope="session", autouse=True)
def migrate_test_db(request):
    """
    Автоматически применяет все миграции к тестовой БД
    только если тест помечен как интеграционный.
    """
    log.debug("INTERGRATION MIGRATIONS TO %s", conf.test_db_url)
    if not any(
        "integration" in marker.name
        for item in request.session.items
        for marker in item.iter_markers()
    ):
        return
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", conf.test_db_url)
    command.upgrade(alembic_cfg, "head")

    yield



