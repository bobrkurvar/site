import pytest
from core.logger import setup_logging
from domain import *

setup_logging()

@pytest.fixture
def domain_handbooks_models_for_products():
    return TileSize, TileSurface, TileColor, Categories, Box, Producer


@pytest.fixture
def domain_handbooks_models_for_collection():
    return Collections, CollectionCategory


