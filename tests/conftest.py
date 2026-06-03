import logging

import pytest

from core.logger import setup_logging, setup_test_logging
from domain import *

setup_test_logging()
# setup_logging()

log = logging.getLogger(__name__)


@pytest.fixture
def domain_handbooks_models_for_products():
    return TileSize, TileSurface, TileColor, Category, Box, Producer


@pytest.fixture
def domain_handbooks_models_for_collection():
    return Collection, CollectionCategory
