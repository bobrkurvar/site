import logging
from decimal import Decimal
from pathlib import Path

from domain import Category, Operation, Slug, Tile, TileSize

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
    if color:
        filters["color_name"] = color
    if size:
        length, width, height = (Decimal(i) for i in size.split())
        tile_size_id = await manager.read_one(
            TileSize, length=length, width=width, height=height
        )
        if tile_size_id:
            filters["size_id"] = tile_size_id.id

    if category is not None:
        category_name = (await manager.read_one(Slug, slug=category)).name
        filters["category_name"] = category_name

    return filters


def build_main_images(tiles):
    main_images = {}
    for tile in tiles:
        path_obj = Path(tile.images[0].image_path)
        parts = path_obj.stem.split("-")
        if len(parts) > 1:
            parts[-1] = "0"
            new_filename = f"{'-'.join(parts)}{path_obj.suffix}"
            main_images[tile.id] = (path_obj.parent / new_filename).as_posix()
        else:
            main_images[tile.id] = path_obj.as_posix()

    return main_images


async def fetch_items(manager, limit, offset, **filters):
    total_items = await manager.read(Tile, loaded=["images", "size", "box"], **filters)
    items = await manager.read(
        Tile, loaded=["images", "size", "box"], limit=limit, offset=offset, **filters
    )
    filters.pop("category_name", None)
    total_count = len(total_items)
    return items, total_count


async def fetch_collections_items(manager, collection_slug, limit, offset, **filters):
    slug_record = await manager.read_one(Slug, slug=collection_slug)
    if not slug_record:
        return [], 0

    collection_name = slug_record.name
    search_pattern = f'%"{collection_name}"%'

    filters["name"] = Operation(value=search_pattern, op="ilike")

    items = await manager.read(
        Tile, loaded=["images", "size", "box"], limit=limit, offset=offset, **filters
    )

    total_count = await manager.count(Tile, **filters)

    return items, total_count


async def get_categories_for_items(manager):
    categories = {cat.name for cat in await manager.read(Category, order_by="name")}
    return await manager.read(Slug, name=categories)
