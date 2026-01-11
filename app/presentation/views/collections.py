import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain import Categories, Collections, Tile, map_to_tile_domain
from repo import Crud, get_db_manager
from services.images import get_image_path
from services.views import (build_data_for_filters, build_main_images,
                            build_tile_filters, fetch_collections_items)

router = APIRouter(tags=["presentation"], prefix="/catalog")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


ITEMS_PER_PAGE = 20


@router.get("/{category}/collections")
async def get_collections_page(
    request: Request,
    manager: dbManagerDep,
    category: str,
    page: int = 1,
):
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit

    category_name = Categories.get_category_from_slug(category)

    collections = await manager.read(
        Collections, category_name=category_name, offset=offset, limit=limit
    )
    collections = [Collections(**collection) for collection in collections]

    total_count = len(await manager.read(Collections, category_name=category_name))
    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await manager.read(Tile, distinct="category_name")
    categories = [Categories(name=category["category_name"]) for category in categories]

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "collections": collections,
            "total_pages": total_pages,
            "categories": categories,
            "page": page,
            "active_tab": "collections",
            "category": category,
        },
    )


@router.get("/{category}/collections/{collection}")
async def get_catalog_tiles_page(
    request: Request,
    manager: dbManagerDep,
    collection: str,
    category: str,
    name: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    filters = await build_tile_filters(manager, name, size, color, category)
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit

    tiles, total_count = await fetch_collections_items(
        manager, collection, limit, offset, **filters
    )
    sizes, colors = await build_data_for_filters(
        manager, collection=collection, category=category
    )
    main_images = build_main_images(tiles)
    tiles = [map_to_tile_domain(tile) for tile in tiles]

    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await manager.read(Tile, distinct="category_name")
    categories = [Categories(name=category["category_name"]) for category in categories]

    path = f"/catalog/{category}/collections/{collection}"

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "products": tiles,
            "colors": colors,
            "sizes": sizes,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "main_images": main_images,
            "categories": categories,
            "path": path,
            "active_tab": "None",
        },
    )
