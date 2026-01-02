import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain import Categories, Tile, map_to_tile_domain
from repo import Crud, get_db_manager
#from services.images import get_image_path
from services.views import (build_main_images,
                            build_tile_filters, fetch_items, build_data_for_filters)

router = APIRouter(tags=["presentation"], prefix="/catalog")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


ITEMS_PER_PAGE = 20


@router.get("/{category}/products/{tile_id:int}")
async def get_tile_page(
    request: Request, category: str, tile_id: int, manager: dbManagerDep
):
    tile = await manager.read(
        Tile,
        to_join=["images", "size", "box"],
        category_name=Categories.get_category_from_slug(category),
        id=tile_id,
    )
    tile = tile[0] if tile else {}
    images = []
    if tile:
        images = tile["images_paths"]
    log.debug("detail images: %s", images)
    tile = map_to_tile_domain(tile)
    categories = await manager.read(Tile, distinct="category_name")
    categories = [Categories(name=category["category_name"]) for category in categories]
    return templates.TemplateResponse(
        "tile_detail.html",
        {
            "request": request,
            "tile": tile,
            "images": images,
            "categories": categories,
        },
    )


@router.get("/{category_name}/products")
async def get_catalog_tiles_page(
    request: Request,
    category_name: str,
    manager: dbManagerDep,
    name: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    filters = await build_tile_filters(manager, name, size, color, category_name)
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit

    tiles, total_count = await fetch_items(manager, limit, offset, **filters)
    sizes, colors = await build_data_for_filters(manager, category_name)
    main_images = build_main_images(tiles)
    tiles = [map_to_tile_domain(tile) for tile in tiles]

    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await manager.read(Tile, distinct="category_name")
    categories = [Categories(name=category["category_name"]) for category in categories]
    path = f"/catalog/{category_name}/products"

    return templates.TemplateResponse(
        "catalog.html",
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
            "category": category_name,
            "path": path,
            "active_tab": "products"
        },
    )
