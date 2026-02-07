from domain import TileSize, TileSurface, TileColor, Categories, Box, Producer
import pytest

@pytest.fixture
def domain_handbooks_models():
    return TileSize, TileSurface, TileColor, Categories, Box, Producer
