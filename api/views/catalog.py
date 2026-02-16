import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from adapters.crud import Crud, get_db_manager
from adapters.images import ProductImagesManager
from core.config import ITEMS_PER_PAGE
from domain import Slug, Tile, map_to_tile_domain
from services.views import (build_data_for_filters, build_main_images,
                            build_tile_filters, fetch_items,
                            get_categories_for_items)

router = APIRouter(tags=["presentation"], prefix="/catalog")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("/{category}/products/{tile_id:int}")
async def get_tile_page(
    request: Request, category: str, tile_id: int, manager: dbManagerDep
):
    product_manager = ProductImagesManager()
    category_name = (await manager.read(Slug, slug=category))[0]["name"]
    tile = await manager.read(
        Tile,
        to_join=["images", "size", "box"],
        category_name=category_name,
        id=tile_id,
    )
    tile = tile[0] if tile else {}
    images = []
    if tile:
        images = [
            product_manager.get_product_details_image_path(i)
            for i in tile["images_paths"]
        ]
    log.debug("detail images: %s", images)
    tile = map_to_tile_domain(**tile)
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
    product_manager = ProductImagesManager()
    for k in main_images:
        main_images[k] = product_manager.get_product_catalog_image_path(main_images[k])

    tiles = [map_to_tile_domain(**tile) for tile in tiles]
    log.debug("main_images: %s", main_images)
    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await get_categories_for_items(manager)

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
            "active_tab": "products",
        },
    )
