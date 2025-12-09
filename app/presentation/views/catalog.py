import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain import Tile, Types, Collections, map_to_tile_domain
from repo import Crud, get_db_manager
from services.views import build_tile_filters, build_main_images, build_sizes_and_colors, fetch_tiles

router = APIRouter(tags=["presentation"], prefix="/catalog")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


ITEMS_PER_PAGE = 1

@router.get("/{category}/{tile_id:int}")
async def get_tile_page(
    request: Request, category: str, tile_id: int, manager: dbManagerDep
):
    tile = await manager.read(
        Tile,
        to_join=["images", "size", "box"],
        type_name=Types.get_category_from_slug(category),
        id=tile_id,
    )
    tile = tile[0] if tile else {}
    images = []
    if tile:
        images = tile["images_paths"]
    log.debug("detail images: %s", images)
    tile = map_to_tile_domain(tile)
    categories = await manager.read(Tile, distinct="type_name")
    categories = [Types(name=category["tile_type"]) for category in categories]
    return templates.TemplateResponse(
        "tile_detail.html",
        {
            "request": request,
            "tile": tile,
            "images": images,
            "categories": categories,
        },
    )


@router.get("/{category}/{collection:str}")
async def get_catalog_tiles_page(
    request: Request,
    category: str,
    manager: dbManagerDep,
    collection: str,
    name: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    filters = await build_tile_filters(manager, category, name, size, color)
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit

    collections, tiles, total_count = await fetch_tiles(manager, limit, offset, collection=collection, **filters)

    sizes, colors = await build_sizes_and_colors(manager, category)
    main_images = build_main_images(tiles)
    tiles = [map_to_tile_domain(tile) for tile in tiles]

    #total_count = len(await manager.read(Tile, **filters))
    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await manager.read(Tile, distinct="type_name")
    categories = [Types(name=category["tile_type"]) for category in categories]

    path = f"/catalog/{category}/{collection}" if not filters else f"/catalog/{category}"

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
            "main_images": main_images,
            "categories": categories,
            "category": category,
            "collections": collections,
            "path": path
        },
    )

@router.get("/{category}")
async def get_catalog_tiles_page(
    request: Request,
    category: str,
    manager: dbManagerDep,
    name: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    filters = await build_tile_filters(manager, category, name, size, color)
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit

    collections, tiles, total_count = await fetch_tiles(manager, limit, offset, **filters)
    collections = [Collections(**collection) for collection in collections]
    sizes, colors = await build_sizes_and_colors(manager, category)
    main_images = build_main_images(tiles)
    tiles = [map_to_tile_domain(tile) for tile in tiles]

    #total_count = len(await manager.read(Tile, **filters))
    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await manager.read(Tile, distinct="type_name")
    categories = [Types(name=category["tile_type"]) for category in categories]
    path = f"/catalog/{category}"

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
            "main_images": main_images,
            "categories": categories,
            "category": category,
            "collections": collections,
            "path": path
        },
    )

