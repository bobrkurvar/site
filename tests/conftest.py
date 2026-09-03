import logging

import pytest

from core.logger import setup_logging, setup_test_logging
from domain import *

setup_test_logging()


log = logging.getLogger(__name__)


@pytest.fixture
def tile():
    return Tile(
        name="Tile",
        size=TileSize(length=300, width=200, height=10),
        color=TileColor("color", "feature"),
        producer=Producer("producer"),
        box=Box(area=1, weight=30),
        boxes_count=3,
        images=[Image(b"MAIN"), Image(b"A"), Image(b"B")],
        surface=TileSurface("surface"),
        category=Category("category"),
    )


# @pytest.fixture
# def collection():
#     return Collection(
#         name="collection",
#         categories=Category("category"),
#         image=Image(image_bytes=b"COLLECTION"),
#     )


@pytest.fixture
def domain_handbooks_models_for_products() -> set:
    return {TileSize, TileSurface, TileColor, Category, Box, Producer}


@pytest.fixture
def domain_handbooks_models_for_collection():
    return Collection, CollectionCategory
