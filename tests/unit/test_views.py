import logging

import pytest
from slugify import slugify

from core.config import ITEMS_PER_PAGE
from domain import Categories, Slug
from services.views import (build_data_for_filters, build_main_images,
                            build_tile_filters, extract_quoted_word,
                            fetch_items)
from tests.unit.conftest import manager_factory

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
    category = "Tile"
    category_slug = slugify(category)
    await manager.create(Slug, name=category, slug=category_slug)
    filters = await build_tile_filters(
        manager, name="tile1", size="1×1×1", color="color1", category=category_slug
    )
    assert filters == {
        "name": "tile1",
        "size_id": 1,
        "color_name": "color1",
        "category_name": category,
    }


@pytest.mark.asyncio
async def test_build_tile_filters_with_not_exists_size(manager_factory):
    manager = await manager_factory()
    category = "Tile"
    category_slug = slugify(category)
    await manager.create(Slug, name=category, slug=category_slug)
    filters = await build_tile_filters(
        manager,
        name="tile1",
        size="300×200×110",
        color="color1",
        category=category_slug,
    )
    assert filters == {
        "name": "tile1",
        "color_name": "color1",
        "category_name": category,
    }  # id размера не найдётся в базе и size_id не будет в фильтрах


@pytest.mark.asyncio
async def test_build_data_for_filters_catalog_with_categories_when_exists_handbooks_not_exists_items(
    manager_factory,
):
    manager = await manager_factory()
    category = "Tile"
    category_slug = slugify(category)
    await manager.create(Slug, name=category, slug=category_slug)
    sizes, colors = await build_data_for_filters(manager, category=category_slug)
    assert sizes == [] and colors == []


@pytest.mark.asyncio
async def test_build_data_for_filters_catalog_with_categories_when_exists_handbooks_and_exists_items(
    manager_factory,
):
    n = 5
    manager = await manager_factory(n)
    category = "category"  # так как фабрика создаёт категорию с таким именем
    category_slug = slugify(category)
    await manager.create(Slug, name=category, slug=category_slug)
    sizes, colors = await build_data_for_filters(manager, category=category_slug)
    assert len(sizes) == n and len(colors) == n


@pytest.mark.asyncio
async def test_build_data_for_filters_catalog_with_categories_when_exists_handbooks_and_exists_items_with_repeats_colors(
    manager_factory,
):
    n = 5
    manager = await manager_factory(n, True)
    category = "category"  # так как фабрика создаёт категорию с таким именем
    category_slug = slugify(category)
    await manager.create(Slug, name=category, slug=category_slug)
    sizes, colors = await build_data_for_filters(manager, category=category_slug)
    assert len(sizes) == n and len(colors) == 1


@pytest.mark.asyncio
async def test_build_main_images():
    image1 = "image-image-110"
    tiles = [{"id": 1, "images_paths": [image1]}]
    assert build_main_images(tiles) == {1: "image-image-0"}
    image2 = "image-image-0"
    tiles = [{"id": 1, "images_paths": [image2]}]
    assert build_main_images(tiles) == {1: "image-image-0"}


@pytest.mark.asyncio
async def test_fetch_items(manager_factory):
    n = 3 * ITEMS_PER_PAGE
    limit = ITEMS_PER_PAGE
    manager = await manager_factory(n)
    pages = (1, 2, 3)
    for page in pages:
        log.debug("page: %s", page)
        offset = (page - 1) * limit
        items, count = await fetch_items(manager, limit, offset)
        assert len(items) == ITEMS_PER_PAGE and count == n
        exp_id = offset + 1
        assert items[0]["id"] == exp_id
