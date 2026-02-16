import pytest

from domain import Box, Categories, Producer, TileColor, TileSize, TileSurface


@pytest.fixture
def domain_handbooks_models():
    return TileSize, TileSurface, TileColor, Categories, Box, Producer
