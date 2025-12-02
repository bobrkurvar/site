import logging
from typing import Annotated
from decimal import Decimal

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain import Tile, TileColor, TileSize, map_to_tile_domain
from repo import Crud, get_db_manager

router = APIRouter(tags=["presentation"], prefix="/catalog")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


ITEMS_PER_PAGE = 20


@router.get("")
async def get_catalog_tiles_page(
    request: Request,
    manager: dbManagerDep,
    name: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    filters = {}
    if name:
        filters["name"] = name
    if color:
        filters["color_name"] = color
    if size:
        length, width, height = (
            Decimal(i) for i in size.split("×")
        )
        tile_size_id = (await manager.read(TileSize, length=length, width=width, height=height))[0]
        filters["tile_size_id"] = tile_size_id["id"]

    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit



    tiles = await manager.read(Tile, to_join=["images", "size", "box"], limit=limit, offset=offset, **filters)
    tile_sizes = await manager.read(Tile, to_join=["size"], distinct="tile_size_id")
    tile_colors = await manager.read(Tile, distinct="color_name")

    sizes = [TileSize(size_id=size["size_id"], height=size['size_height'], width=size['size_width'], length=size["size_length"]) for size in tile_sizes]
    colors = [dict(color_name=color["color_name"], feature_name=color["feature_name"]) for color in tile_colors]

    for t in tiles:
        log.debug("images: %s", t['images_paths'])

    main_images = {}

    for tile in tiles:
        img = tile['images_paths'][0]
        main_images[tile['id']] = img[:-2] + '-0'

    log.debug("main_images: %s", main_images)

    tiles = [map_to_tile_domain(tile) for tile in tiles]

    # sizes = await manager.read(TileSize)
    # sizes = [TileSize(size_id=size["id"], height=size['height'], width=size['width'], length=size["length"]) for size in sizes]
    #colors = await manager.read(TileColor)

    total_count = len(await manager.read(Tile, **filters))
    total_pages = max((total_count + limit - 1) // limit, 1)

    return templates.TemplateResponse(
        "tiles_catalog.html",
        {
            "request": request,
            "tiles": tiles,
            "colors": colors,
            "sizes": sizes,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "main_images": main_images
        },
    )


@router.get("/{tile_id}")
async def get_tile_page(request: Request, tile_id: int, manager: dbManagerDep):
    tile = await manager.read(Tile, to_join=["images", "size", "box"], id=tile_id)
    tile = tile[0] if tile else {}
    images = []
    if tile: images = tile["images_paths"]
    log.debug("detail images: %s", images)
    tile = map_to_tile_domain(tile)
    return templates.TemplateResponse(
        "tile_detail.html",
        {
            "request": request,
            "tile": tile,
            "images": images
        },
    )

