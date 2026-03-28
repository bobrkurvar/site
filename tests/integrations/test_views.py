import pytest
from services.views import build_data_for_filters
from slugify import slugify
from domain import Slug
#from .conftest import products_env_with_tiles, products_env

@pytest.mark.asyncio
async def test_build_data_for_filters_catalog_with_categories_when_exists_handbooks_not_exists_items(
    products_env,
):
    manager, _ = products_env
    category = "category"
    category_slug = slugify(category)
    await manager.create(Slug, name=category, slug=category_slug)
    sizes, colors, producers = await build_data_for_filters(
        manager, category=category_slug
    )
    assert not sizes and not colors and not producers


@pytest.mark.asyncio
async def test_build_data_for_filters_with_category(
    products_env_with_tiles,
):
    categories = {"category1": 3, "category2": 4}
    manager = await products_env_with_tiles(categories)
    category2_slug = (await manager.read(Slug, name="category2"))[0]["slug"]
    sizes, colors, producers = await build_data_for_filters(manager, category=category2_slug)
    assert len(sizes) == len(colors) == len(producers) == 4


@pytest.mark.asyncio
async def test_build_data_for_filters_with_category_and_collection(
    products_env_with_tiles,
):
    categories = {"category1": 7, "category2": 4}
    categories_with_collections = {"category1": "collection1", "category2": "collection2"}
    manager = await products_env_with_tiles(categories, categories_with_collections)
    category1_slug = (await manager.read(Slug, name="category1"))[0]["slug"]
    category2_slug = (await manager.read(Slug, name="category2"))[0]["slug"]
    sizes1, colors1, producers1 = await build_data_for_filters(manager, category=category1_slug)
    sizes2, colors2, producers2 = await build_data_for_filters(manager, category=category2_slug)
    assert len(sizes1) == len(colors1) == len(producers1) == 7
    assert len(sizes2) == len(colors2) == len(producers2) == 4