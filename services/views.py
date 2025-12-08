from domain import Types, Tile, TileSize, TileColor, Collections
from decimal import Decimal
import logging

log = logging.getLogger(__name__)

def build_tile_filters(
    category: str | None, name: str | None, size: str | None, color: str | None
) -> dict:
    filters = {}
    if name:
        filters["name"] = name
    if color:
        filters["color_name"] = color
    if size:
        length, width, height = (Decimal(i) for i in size.split("×"))
        filters["tile_size_tuple"] = (length, width, height)
    if category is not None:
        filters["type_name"] = Types.get_category_from_slug(category)
    return filters


def build_sizes_and_colors(tile_sizes, tile_colors):
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
        main_images[tile["id"]] = img[:-2] + "-0"
    return main_images


def extract_quoted_word(name: str) -> str | None:
    parts = name.split('"')
    log.debug("prats: %s", parts)
    if len(parts) >= 3:
        log.debug("parts[1]: %s", parts[1].lower())
        return parts[1].lower()  # слово между первой и второй кавычкой
    return None

async def fetch_tiles(manager, limit, offset, category = None, page = 1, **filters):

    if category:
        filters.update({"tile_type": category})

    tile_sizes = await manager.read(
        Tile, to_join=["size"], distinct="tile_size_id", **filters
    )
    tile_colors = await manager.read(Tile, distinct="color_name", **filters)

    tiles = await manager.read(
        Tile, to_join=["images", "size", "box"], limit=limit, offset=offset, **filters
    )

    if category:
        colls = await manager.read(Collections, category=category)
        colls_names = [coll["name"] for coll in colls]
        log.debug("category: %s colls: %s", category, colls_names)
        tiles = [tile for tile in tiles if extract_quoted_word(tile["name"]) not in colls_names]
        tile_colors = [tile for tile in tile_colors if extract_quoted_word(tile["name"]) not in colls_names]
        tile_sizes = [tile_size for tile_size in tile_sizes if extract_quoted_word(tile_size["name"]) not in colls_names]
    else:
        colls = await manager.read(Collections)
        colls_names = [coll["name"] for coll in colls]
        log.debug("colls: %s",colls_names)
        tiles = [tile for tile in tiles if extract_quoted_word(tile["name"]) in colls_names]
        tile_colors = [tile for tile in tile_colors if extract_quoted_word(tile["name"]) in colls_names]
        tile_sizes = [tile_size for tile_size in tile_sizes if extract_quoted_word(tile_size["name"]) in colls_names]
        colls = []


    return colls, tiles, tile_sizes, tile_colors, #total_count

