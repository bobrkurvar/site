from services.views import get_collections_filtered_by_category, get_catalog, CatalogPage
import pytest
from domain import NotFoundError


async def test_get_collections_from_category(uow_fix, make_categories, make_collections):
    category1, category2 = await make_categories(2)
    expected = await make_collections(categories=category1, count=2)
    await make_collections(categories=category2, count=3)

    async with uow_fix as uow:
        collections, total_count = await get_collections_filtered_by_category(
            db=uow.db,
            category_id=category1.id,
        )

    assert {c.id for c in collections} == {c.id for c in expected}
    assert total_count == 2


async def test_get_product_catalog_from_category(uow_fix, make_categories, make_tiles):
    category1, category2 = await make_categories(2)
    expected = await make_tiles(category_id=category1.id, count=3)
    await make_tiles(category_id=category2.id, count=2)

    page: CatalogPage = await get_catalog(uow=uow_fix, category_id=category1.id)

    assert {tile.id for tile in page.tiles} == {tile.id for tile in expected}
    assert page.total_count == 3


async def test_get_product_catalog_from_category_and_collection(uow_fix, make_categories, make_collections, make_tiles):
    category1, category2 = await make_categories(2)
    collection1, collection2 = await make_collections(count=2, categories=category1)
    expected = await make_tiles(category_id=category1.id, collection_name=collection1.name, count=3)
    # та же коллекция, но другая категория
    await make_tiles(category_id=category2.id, collection_name=collection1.name, count=2)
    # та же категория, но другая коллекция
    await make_tiles(category_id=category1.id, collection_name=collection2.name, count=2)

    page: CatalogPage = await get_catalog(uow=uow_fix, category_id=category1.id, collection_id=collection1.id)

    assert {tile.id for tile in page.tiles} == {tile.id for tile in expected}
    assert all(tile.category_id == category1.id for tile in page.tiles)
    assert all(f'"{collection1.name}"' in tile.name for tile in page.tiles)
    assert page.total_count == 3


async def test_get_product_catalog_from_category_and_collection_without_relation(uow_fix, make_categories, make_collections, make_tiles):
    category1, category2 = await make_categories(2)
    collection1, = await make_collections(categories=category1)
    with pytest.raises(NotFoundError):
        await get_catalog(uow=uow_fix, category_id=category2.id, collection_id=collection1.id)
