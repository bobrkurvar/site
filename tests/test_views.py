import logging

import pytest
from tests.conftest import manager_factory

from domain import Categories
from services.views import build_main_images, fetch_items, extract_quoted_word, build_tile_filters, build_data_for_filters


log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_extract_quoted_word_collection_name():
    name1 = 'tile5 "collection"'
    name2 = 'tile5 "COllection"'
    collection = "collection"
    col_from_name1 = extract_quoted_word(name1)
    col_from_name2 = extract_quoted_word(name2)
    assert col_from_name1 == collection and col_from_name2 == collection


@pytest.mark.asyncio
async def test_build_tile_filters_with_exists_size(manager_factory):
    manager = await manager_factory(1)
    category = Categories("Tile") # что бы зарегистрировать slug и его обратное слово
    filters = await build_tile_filters(manager, name="tile1", size="1×1×1", color="color1", category=category.slug)
    assert filters == {"name": "tile1", "size_id": 1, "color_name": "color1", "category_name": category.name}


@pytest.mark.asyncio
async def test_build_tile_filters_with_not_exists_size(manager_factory):
    manager = await manager_factory()
    category = Categories("Tile") # что бы зарегистрировать slug и его обратное слово
    filters = await build_tile_filters(manager, name="tile1", size="300×200×110", color="color1", category=category.slug)
    assert filters == {"name": "tile1", "color_name": "color1", "category_name": category.name} #id размера не найдётся в базе и size_id не будет в фильтрах

@pytest.mark.asyncio
async def test_build_data_for_filters_catalog_with_categories_when_exists_handbooks_not_exists_items(manager_factory):
    manager = await manager_factory()
    category = Categories("tile")
    sizes, colors = await build_data_for_filters(manager, category=category.slug)
    assert sizes == [] and colors == []


@pytest.mark.asyncio
async def test_build_data_for_filters_catalog_with_categories_when_exists_handbooks_and_exists_items(manager_factory):
    n = 5
    manager = await manager_factory(n)
    category = Categories("category")
    sizes, colors = await build_data_for_filters(manager, category=category.slug)
    assert len(sizes) == n and len(colors) == n