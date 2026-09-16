import logging

import pytest

from core.logger import setup_test_logging
from .helpers import create_tiles, make_default_tile
import itertools
from domain import *

setup_test_logging()


log = logging.getLogger(__name__)


@pytest.fixture
def tile():
    return make_default_tile()


@pytest.fixture
def make_categories(uow_fix):
    sequence = itertools.count()

    async def factory(count: int = 1):
        categories = [
            Category(name=f"category-{next(sequence)}")
            for _ in range(count)
        ]

        async with uow_fix as uow:
            return await uow.db.create(seq_data=categories)

    return factory


@pytest.fixture
def make_collections(uow_fix):
    sequence = itertools.count()

    async def factory(
        categories: Category | list[Category],
        count: int = 1,
    ):
        if isinstance(categories, Category):
            categories = [categories]

        collections = []
        async with uow_fix as uow:
            for _ in range(count):
                index = next(sequence)
                collection = Collection(
                    name=f"collection-{index}",
                    image=Image(image_path=f"collection-{index}.jpg"),
                    categories=categories,
                )
                collections.append(await uow.db.save(collection))
        return collections


    return factory


@pytest.fixture
def make_tiles(uow_fix):
    handbooks = None
    async def wrapper(category_id: int | None = None, collection_name: str | None = None, count: int = 1):
        nonlocal handbooks
        tiles, handbooks = await create_tiles(
            uow=uow_fix,
            category_id=category_id,
            collection_name=collection_name,
            count=count,
            handbooks=handbooks
        )
        return tiles
    return wrapper



@pytest.fixture
def domain_handbooks_models_for_products() -> set:
    return {Size, Surface, Color, Category, Box, Producer}


@pytest.fixture
def domain_handbooks_models_for_collection():
    return Collection, CollectionCategory
