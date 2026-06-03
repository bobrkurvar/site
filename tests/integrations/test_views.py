import pytest

# from services.views import build_data_for_filters
from domain import Slug


@pytest.mark.asyncio
async def test_build_data_for_filters_catalog_with_categories_when_exists_handbooks_not_exists_items(
    products_env, query_service
):
    manager, _ = products_env
    slug = await manager.create(Slug(name="category"))
    # sizes, colors, producers = await build_data_for_filters(
    #     manager, category=slug.slug
    # )
    filters = await query_service.get_catalog_filters(category_slug=slug.slug)
    assert not filters.sizes and not filters.colors and not filters.producers


@pytest.mark.asyncio
async def test_build_data_for_filters_with_category(
    products_env_with_tiles, query_service
):
    categories = {"category1": 3, "category2": 4}
    manager = await products_env_with_tiles(categories)
    slug = await manager.read_one(Slug, name="category2")
    # sizes, colors, producers = await build_data_for_filters(
    #     manager, category=category2_slug
    # )
    filters = await query_service.get_catalog_filters(category_slug=slug.slug)
    assert len(filters.sizes) == len(filters.colors) == len(filters.producers) == 4


@pytest.mark.asyncio
async def test_build_data_for_filters_with_category_and_collection(
    products_env_with_tiles, query_service
):
    categories = {"category1": 7, "category2": 4}
    categories_with_collections = {
        "category1": "collection1",
        "category2": "collection2",
    }
    manager = await products_env_with_tiles(categories, categories_with_collections)
    category1_slug = (await manager.read_one(Slug, name="category1")).slug
    category2_slug = (await manager.read_one(Slug, name="category2")).slug
    # sizes1, colors1, producers1 = await build_data_for_filters(
    #     manager, category=category1_slug
    # )
    # sizes2, colors2, producers2 = await build_data_for_filters(
    #     manager, category=category2_slug
    # )
    filters1 = await query_service.get_catalog_filters(category_slug=category1_slug)
    filters2 = await query_service.get_catalog_filters(category_slug=category2_slug)
    assert len(filters1.sizes) == len(filters1.colors) == len(filters1.producers) == 7
    assert len(filters2.sizes) == len(filters2.colors) == len(filters2.producers) == 4
