import pytest
from fakes import FakeUoW, FakeCRUD, FakeStorage
from services.tile import add_tile
from decimal import Decimal
from domain import *

@pytest.fixture
def storage_with_filled_handbooks():
    storage = FakeStorage()
    storage.register_tables(TileSize, TileSurface, TileImages, TileColor, Producer, Types)
    storage.tables[TileSize].update(length=Decimal(300), width=Decimal(200), height=Decimal(10))
    storage.tables[TileSurface].update(name="surface")
    storage.tables[TileImages].update(image_path='path')
    storage.tables[TileColor].update(color_name='color', feature_name='feature_name')
    storage.tables[Producer].update(name='producer')
    storage.tables[Types].update(name="category")
    return storage

@pytest.fixture
def get_manager():
    return FakeCRUD()


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_exists():



