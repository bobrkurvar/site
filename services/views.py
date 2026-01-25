import logging
from decimal import Decimal

from domain import Categories, Collections, Tile, TileColor, TileSize

log = logging.getLogger(__name__)


async def build_tile_filters(
    manager,
    name: str | None,
    size: str | None,
    color: str | None,
    category: str | None = None,
) -> dict:
    filters = {}
    if name:
        filters["name"] = name
    if color:
        filters["color_name"] = color
    if size:
        length, width, height = (Decimal(i) for i in size.split("×"))
        tile_size_id = (
            await manager.read(TileSize, length=length, width=width, height=height)
        )
        if len(tile_size_id) != 0:
            tile_size_id = tile_size_id[0]
            filters["size_id"] = tile_size_id["id"]

    if category is not None:
        filters["category_name"] = Categories.get_category_from_slug(category)

    return filters


async def build_data_for_filters(
    manager, category: str | None = None, collection: str | None = None
):
    category = Categories.get_category_from_slug(category) if category else None
    if collection is not None:
        collection = Collections.get_collection_from_slug(collection).lower()
        log.debug("collection: %s", collection)
        seen = set()
        tile_sizes = await manager.read(Tile, to_join=["size"], category_name=category)
        unique = []
        for tile in tile_sizes:
            if (
                extract_quoted_word(tile["name"]) == collection
                and tile["size_id"] not in seen
            ):
                unique.append(tile)
                seen.add(tile["size_id"])
        tile_sizes = unique

        seen = set()
        unique = []
        tile_colors = await manager.read(Tile, category_name=category)
        for tile in tile_colors:
            if (
                extract_quoted_word(tile["name"]) == collection
                and tile["color_name"] not in seen
            ):
                unique.append(tile)
                seen.add(tile["color_name"])
        tile_colors = unique
        # log.debug("tile_colors before collections: %s", tile_colors)
    else:
        filters = {"category_name": category} if category else {}
        log.debug("filters: %s", filters)
        tile_sizes = await manager.read(
            Tile, to_join=["size"], distinct="size_id", **filters
        )
        tile_colors = await manager.read(Tile, distinct="color_name", **filters)
        #log.debug("tile_sizes before collection filter: %s", tile_sizes)

    sizes = [
        TileSize(
            size_id=size["size_id"],
            height=size["size_height"],
            width=size["size_width"],
            length=size["size_length"],
        )
        for size in tile_sizes
    ]
    colors = [
        TileColor(color_name=color["color_name"], feature_name=color["feature_name"])
        for color in tile_colors
    ]
    return sizes, colors


def build_main_images(tiles):
    main_images = {}
    for tile in tiles:
        img = tile["images_paths"][0]
        log.debug("image: %s", img)
        images_part = img.split("-")
        images_part[-1] = "0"
        main_images[tile["id"]] = "-".join(images_part)
        #main_images[tile["id"]] = img[:-2] + "-0"
    return main_images


def extract_quoted_word(name: str) -> str | None:
    parts = name.split('"')
    if len(parts) >= 3:
        return parts[1].lower()
    return None


async def fetch_items(manager, limit, offset, **filters):

    total_items = await manager.read(Tile, to_join=["images", "size", "box"], **filters)
    items = await manager.read(
        Tile, to_join=["images", "size", "box"], limit=limit, offset=offset, **filters
    )

    filters.pop("category_name", None)
    total_count = len(total_items)

    return items, total_count


async def fetch_collections_items(manager, collection, limit, offset, **filters):
    log.debug("offset: %s, limit: %s", offset, limit)
    log.debug("filters: %s", filters)
    items = await manager.read(
        Tile, to_join=["images", "size", "box"], **filters
    )
    collection = Collections.get_collection_from_slug(collection).lower()
    items = [item for item in items if extract_quoted_word(item["name"]) == collection]
    total_count = len(items)
    log.debug("collection total count: %s", total_count)

    items = items[offset : offset + limit]
    log.debug("collection count: %s", items)

    return items, total_count
