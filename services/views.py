from domain import Types, Tile, TileSize, TileColor, Collections
from decimal import Decimal
import logging

log = logging.getLogger(__name__)

async def build_tile_filters(
    manager, category: str | None, name: str | None, size: str | None, color: str | None
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
        )[0]
        filters["tile_size_id"] = tile_size_id["id"]

    if category is not None:
        filters["type_name"] = Types.get_category_from_slug(category)
    return filters


async def build_sizes_and_colors(manager, category: str):
    category = Types.get_category_from_slug(category)
    tile_sizes = await manager.read(
        Tile, to_join=["size"], distinct="tile_size_id", type_name=category
    )
    tile_colors = await manager.read(Tile, distinct="color_name",  type_name=category)

    log.debug("sizes: %s", tile_sizes)
    log.debug("colors: %s", tile_colors)

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
    if len(parts) >= 3:
        return parts[1].lower()
    return None

async def fetch_tiles(manager, limit, offset, page = 1, collection = None, **filters):
    category = None if "type_name" not in filters else filters["type_name"]
    log.debug("filters: %s", filters)


    tiles = await manager.read(
        Tile, to_join=["images", "size", "box"], limit=limit, offset=offset, **filters
    )

    if category: filters.pop("type_name")
    colls = []
    log.debug("collection: %s", collection)

    total_count = len(tiles)


    if not filters and offset == 0:
        if not collection:
            colls = await manager.read(Collections, category=category)
            colls_names = [coll["name"].lower() for coll in colls]
            log.debug("category: %s colls: %s", category, colls_names)
            tiles = [tile for tile in tiles if extract_quoted_word(tile["name"]) not in colls_names]

            all_category_tiles = await manager.read(Tile, type_name=category)
            in_collections = [tile for tile in tiles if extract_quoted_word(tile["name"]) in colls_names]
            total_count = len(all_category_tiles) - len(in_collections)
            log.debug("total count: %s", total_count)
        else:
            collection = Collections.get_category_from_slug(collection).lower()
            tiles = [tile for tile in tiles if extract_quoted_word(tile["name"]) == collection]
            total_count = len(tiles)
            log.debug("collection total count: %s", total_count)
            colls = []


    return colls, tiles, total_count

