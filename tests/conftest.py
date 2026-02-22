import pytest

from domain import Box, Categories, Producer, TileColor, TileSize, TileSurface
from core.logger import setup_logging

setup_logging()


@pytest.fixture
def domain_handbooks_models():
    return TileSize, TileSurface, TileColor, Categories, Box, Producer
