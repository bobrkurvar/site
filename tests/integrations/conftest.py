from alembic import command
from alembic.config import Config
from adapters.crud import get_db_manager
from adapters.files import FileManager
from core import conf
import logging
import pytest
from sqlalchemy import text


log = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
async def clean_db_after_test(request):
    engine = get_db_manager(test=True)._engine
    if request.node.get_closest_marker("integration") is None:
        return

    yield

    async with engine.begin() as conn:
        await conn.execute(text("""
            TRUNCATE
                tile_images,
                categories,
                producers,
                tile_sizes,
                boxes,
                catalog,
                tile_colors,
                collections,
                tile_surface
                
            RESTART IDENTITY CASCADE;
        """))


@pytest.fixture(autouse=True)
async def clean_fs_after_test(request):
    engine = get_db_manager(test=True)._engine
    if request.node.get_closest_marker("integration") is None:
        return

    yield



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
    alembic_cfg.set_main_option("sqlalchemy.url", conf.db_url)
    command.upgrade(alembic_cfg, "head")

    yield

