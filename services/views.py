import logging
from decimal import Decimal

from domain import (
    Operation,
    Tile,
    Size,
    Operations,
    Collection,
    Category,
    CollectionCategory,
    DomainFilter
)
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class CatalogPage:
    tiles: list[Tile]
    total_count: int
    category: Category
    collection: Collection | None

async def build_tile_filters(
    manager,
    producer: str | None,
    size: str | None,
    color: str | None,
) -> dict:
    filters = {}
    if producer:
        filters["producer_name"] = producer
    if color:
        filters["color_name"] = color
    if size:
        length, width, height = (Decimal(i) for i in size.split())
        size = await manager.read_one(Size, length=length, width=width, height=height)
        filters["size_id"] = size.id

    return filters


async def fetch_items(db, limit, offset, category_id: int, **filters):
    total_count = await db.count(
        Tile,
        category_id=category_id,
        **filters,
    )

    items = await db.read(
        Tile,
        loaded=["images", "size", "box"],
        category_id=category_id,
        limit=limit,
        offset=offset,
        **filters,
    )

    return items, total_count


async def fetch_collections_items(
    db,
    collection_name: str,
    category_id: int,
    limit: int,
    offset: int,
    **filters,
):
    search_pattern = f'%"{collection_name}"%'

    filters["name"] = Operation(
        value=search_pattern,
        op=Operations.ilike,
    )
    items, total_count = await fetch_items(
        db=db,
        category_id=category_id,
        limit=limit,
        offset=offset,
        **filters
    )

    # items = await manager.read(
    #     Tile,
    #     loaded=["images", "size", "box"],
    #     limit=limit,
    #     offset=offset,
    #     category_id=category_id,
    #     **filters,
    # )
    #
    # total_count = await manager.count(Tile, category_id=category_id, **filters)

    return items, total_count


async def read_catalog_context(
    db,
    category_id: int,
    collection_id: int | None = None,
) -> tuple[Category, Collection | None]:
    collection = None
    category = await db.read_one(
        Category,
        id=category_id,
        with_raise=True,
    )
    if collection_id is not None:
        collection = await db.read_one(
            Collection,
            id=collection_id,
            with_raise=True,
        )

        await db.read_one(
            CollectionCategory,
            collection_id=collection_id,
            category_id=category_id,
            with_raise=True,
        )

    return category, collection


async def get_catalog(
    uow,
    category_id: int,
    limit: int,
    offset: int,
    collection_id: int | None = None,
    **filters,
) -> CatalogPage:
    async with uow:
        context = await read_catalog_context(
            uow.db,
            category_id=category_id,
            collection_id=collection_id,
        )
        category, collection = context


        if collection is not None:
            tiles, total_count = await fetch_collections_items(
                uow.db,
                collection.name,
                limit,
                offset,
                **filters,
            )
        else:
            tiles, total_count = await fetch_items(
                db=uow.db,
                limit=limit,
                offset=offset,
                category_id=category_id,
                **filters,
            )

    return CatalogPage(tiles, total_count, category, collection)


async def get_collections_filtered_by_category(
    db,
    category_id: int,
    offset: int,
    limit: int,
) -> tuple[tuple[Collection, ...], int]:
    await db.read_one(
        Category,
        id=category_id,
        with_raise=True,
    )

    collections = await db.read(
        Collection,
        domain_filters=[
            DomainFilter(
                model=CollectionCategory,
                field="category_id",
                value=category_id,
            )
        ],
        offset=offset,
        limit=limit,
    )

    total_count = await db.count(
        CollectionCategory,
        category_id=category_id,
    )

    return collections, total_count