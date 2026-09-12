import logging

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from adapters.deps import UowDep
from core.config import ITEMS_PER_PAGE
from domain import Tile, Category
from services.views import build_tile_filters, get_catalog, CatalogPage
from api.schemas import ProductCatalogOut, ProductDetailsOut

router = APIRouter(tags=["presentation"], prefix="/catalog")
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("/products/{article:int}")
async def get_tile_page(request: Request, article: int, uow: UowDep):
    #product_manager = ProductImagesManager()
    async with uow:
        tile = await uow.db.read_one(
            Tile,
            loaded=["images", "size", "box"],
            id=article,
            with_raise=True
        )
        # if tile:
        #     images = await asyncio.gather(
        #         *(
        #             product_manager.get_product_details_image_path(image.image_path)
        #             for image in tile.images
        #         )
        #     )
        #     tile.set_images(images)
        categories = await uow.db.read(Category)
    tile = ProductDetailsOut(tile=tile)
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
    #query_service: QueryServiceDep,
    producer: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    limit = ITEMS_PER_PAGE
    offset = (page - 1) * limit
    async with uow:
        filters = await build_tile_filters(
            producer=producer, color=color, size=size, manager=uow.db
        )
        categories = await uow.db.read(Category, order_by="name")
        filter_options = await uow.query_service.get_catalog_filters(
            category_id=category_id,
        )

    catalog_page: CatalogPage = await get_catalog(
        uow=uow, category_id=category_id, limit=limit, offset=offset, **filters
    )


    # product_manager = ProductImagesManager()
    # for tile in page.tiles:
    #     resolved_paths = await asyncio.gather(
    #         *(
    #             product_manager.get_product_catalog_image_path(path)
    #             for path in tile.images_paths
    #         )
    #     )
    #     tile.set_images(resolved_paths)
    tiles = [ProductCatalogOut(tile=tile) for tile in catalog_page.tiles]

    total_pages = max((catalog_page.total_count + limit - 1) // limit, 1)
    category_path = f"{category_slug}/{category_id}"

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "tiles": tiles,
            "page": page,
            "total_pages": total_pages,
            "total_count": catalog_page.total_count,
            "categories": categories,
            "category_path": category_path,
            "filters": filter_options,
            "active_tab": "products",
        },
    )
