import logging

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from adapters.deps import DbManagerDep, QueryServiceDep
from adapters.images import ProductImagesManager
from core.config import ITEMS_PER_PAGE
from domain import Slug, Tile
from services.views import (
    build_main_images,
    build_tile_filters,
    fetch_items,
    get_categories_for_items,
)

router = APIRouter(tags=["presentation"], prefix="/catalog")
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("/{category}/products/{tile_id:int}")
async def get_tile_page(
    request: Request, category: str, tile_id: int, manager: DbManagerDep
):
    product_manager = ProductImagesManager()
    category_name = (await manager.read_one(Slug, slug=category)).name
    tile = await manager.read_one(
        Tile,
        loaded=["images", "size", "box"],
        category_name=category_name,
        id=tile_id,
    )
    images = []
    if tile:
        images = [
            await product_manager.get_product_details_image_path(i.image_path)
            for i in tile.images
        ]
    log.debug("detail images: %s", images)
    categories = await get_categories_for_items(manager)
    return templates.TemplateResponse(
        "tile_detail.html",
        {
            "request": request,
            "tile": tile,
            "images": images,
            "categories": categories,
        },
    )


@router.get("/{category_slug}/products")
async def get_catalog_tiles_page(
    request: Request,
    category_slug: str,
    manager: DbManagerDep,
    query_service: QueryServiceDep,
    producer: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    filters = await build_tile_filters(manager, producer, size, color, category_slug)
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit
    tiles, total_count = await fetch_items(manager, limit, offset, **filters)
    filters = await query_service.get_catalog_filters(category_slug=category_slug)
    main_images = build_main_images(tiles)
    product_manager = ProductImagesManager()
    for k in main_images:
        main_images[k] = await product_manager.get_product_catalog_image_path(main_images[k])

    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await get_categories_for_items(manager)

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "tiles": tiles,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "main_images": main_images,
            "categories": categories,
            "category": category_slug,
            "filters": filters,
            "active_tab": "products",
        },
    )
