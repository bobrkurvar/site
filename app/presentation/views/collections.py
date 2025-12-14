import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain import Categories, Collections, Tile, map_to_tile_domain
from repo import Crud, get_db_manager
from services.views import (build_main_images, build_sizes_and_colors,
                            build_tile_filters, fetch_collections_items)

router = APIRouter(tags=["presentation"], prefix="/collections")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


ITEMS_PER_PAGE = 20


@router.get("")
async def get_collections_page(
    request: Request,
    manager: dbManagerDep,
    page: int = 1,
):
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit

    collections = await manager.read(Collections, offset=offset, limit=limit)
    collections = [Collections(**collection) for collection in collections]

    total_count = len(await manager.read(Collections))
    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await manager.read(Tile, distinct="category_name")
    categories = [Categories(name=category["category_name"]) for category in categories]

    return templates.TemplateResponse(
        "collections.html",
        {
            "request": request,
            "collections": collections,
            "total_pages": total_pages,
            "categories": categories,
            "page": page,
        },
    )


@router.get("/{collection}")
async def get_catalog_tiles_page(
    request: Request,
    manager: dbManagerDep,
    collection: str,
    name: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    filters = await build_tile_filters(manager, name, size, color)
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit

    tiles, total_count = await fetch_collections_items(
        manager, collection, limit, offset, **filters
    )
    sizes, colors = await build_sizes_and_colors(manager, collection=collection)
    main_images = build_main_images(tiles)
    tiles = [map_to_tile_domain(tile) for tile in tiles]

    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await manager.read(Tile, distinct="category_name")
    categories = [Categories(name=category["category_name"]) for category in categories]

    path = f"/collections/{collection}"

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
            "path": path,
        },
    )
