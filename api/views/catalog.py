import logging

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from adapters.deps import UowDep, QueryServiceDep
from adapters.images import ProductImagesManager
from core.config import ITEMS_PER_PAGE
from domain import Tile, Category
from services.views import build_tile_filters, fetch_items
import asyncio

router = APIRouter(tags=["presentation"], prefix="/catalog")
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("/products/{article:int}")
async def get_tile_page(request: Request, article: int, uow: UowDep):
    product_manager = ProductImagesManager()
    async with uow:
        tile = await uow.db.read_one(
            Tile,
            loaded=["images", "size", "box"],
            id=article,
        )
        if tile:
            # images = [
            #     await product_manager.get_product_details_image_path(i.image_path)
            #     for i in tile.images
            # ]
            # tile.set_images(images)
            images = await asyncio.gather(
                *(
                    product_manager.get_product_details_image_path(image.image_path)
                    for image in tile.images
                )
            )
            tile.set_images(images)
        categories = await uow.db.read(Category)
    return templates.TemplateResponse(
        "tile_detail.html",
        {
            "request": request,
            "tile": tile,
            "categories": categories,
        },
    )


@router.get("/{category_slug}/{category_id:int}/products")
async def get_catalog_tiles_page(
    request: Request,
    category_slug: str,
    category_id: int,
    uow: UowDep,
    query_service: QueryServiceDep,
    producer: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit

    async with uow:
        category = await uow.db.read_one(
            Category,
            id=category_id,
            with_raise=True,
        )

        tile_filters = await build_tile_filters(
            uow.db,
            producer,
            size,
            color,
            category.name,
        )

        tiles, total_count = await fetch_items(
            uow.db,
            limit,
            offset,
            **tile_filters,
        )

        categories = await uow.db.read(Category, order_by="name")

    filter_options = await query_service.get_catalog_filters(
        category_name=category.name,
    )

    product_manager = ProductImagesManager()
    for tile in tiles:
        resolved_paths = await asyncio.gather(
            *(
                product_manager.get_product_catalog_image_path(path)
                for path in tile.images_paths
            )
        )
        tile.set_images(resolved_paths)

    total_pages = max((total_count + limit - 1) // limit, 1)
    category_path = f"{category_slug}/{category_id}"

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "tiles": tiles,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "categories": categories,
            "category_path": category_path,
            "filters": filter_options,
            "active_tab": "products",
        },
    )
