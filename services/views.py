import logging
from decimal import Decimal

from domain import Operation, Tile, TileSize, Operations

log = logging.getLogger(__name__)


async def build_tile_filters(
    manager,
    producer: str | None,
    size: str | None,
    color: str | None,
    category: str | None = None,
) -> dict:
    filters = {}
    if producer:
        filters["producer_name"] = producer
    if category:
        filters["category_name"] = category
    if color:
        filters["color_name"] = color
    if size:
        length, width, height = (Decimal(i) for i in size.split())
        tile_size_id = await manager.read_one(
            TileSize, length=length, width=width, height=height
        )
        if tile_size_id:
            filters["size_id"] = tile_size_id.id

    return filters




async def fetch_items(manager, limit, offset, **filters):
    total_items = await manager.read(Tile, loaded=["images", "size", "box"], **filters)
    items = await manager.read(
        Tile, loaded=["images", "size", "box"], limit=limit, offset=offset, **filters
    )
    filters.pop("category_name", None)
    total_count = len(total_items)
    return items, total_count


async def fetch_collections_items(
    manager,
    collection_name: str,
    limit: int,
    offset: int,
    **filters,
):
    search_pattern = f'%"{collection_name}"%'

    filters["name"] = Operation(
        value=search_pattern,
        op=Operations.ilike,
    )

    items = await manager.read(
        Tile,
        loaded=["images", "size", "box"],
        limit=limit,
        offset=offset,
        **filters,
    )

    total_count = await manager.count(Tile, **filters)

    return items, total_count


