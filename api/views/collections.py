import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from adapters.crud import Crud, get_db_manager
from adapters.images import CollectionImagesManager, ProductImagesManager
from core.config import COLLECTIONS_PER_PAGE
from domain import CollectionCategory, Slug, map_to_tile_domain
from services.views import (build_data_for_filters, build_main_images,
                            build_tile_filters, fetch_collections_items,
                            get_categories_for_items)

router = APIRouter(tags=["presentation"], prefix="/catalog")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("/{category}/collections")
async def get_collections_page(
    request: Request,
    manager: dbManagerDep,
    category: str,
    page: int = 1,
):
    limit = COLLECTIONS_PER_PAGE
    offset = (page - 1) * limit
    log.debug("category: %s", category)
    category_name = (await manager.read(Slug, slug=category))[0]["name"]
    category_collections = await manager.read(
        CollectionCategory,
        category_name=category_name,
        offset=offset,
        limit=limit,
        to_join=["collection"],
    )
    collections = []
    collection_manager = CollectionImagesManager()
    for coll in category_collections:
        coll["image_path"] = collection_manager.get_collections_image_path(
            coll["image_path"]
        )
        coll["name"] = coll["collection_name"]
        slug = (await manager.read(Slug, name=coll["name"]))[0]["slug"]
        coll["slug"] = slug
        collections.append(coll)
    total_count = len(
        await manager.read(CollectionCategory, category_name=category_name)
    )
    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await get_categories_for_items(manager)

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
    limit = COLLECTIONS_PER_PAGE
    offset = (page - 1) * limit

    tiles, total_count = await fetch_collections_items(
        manager, collection, limit, offset, **filters
    )

    sizes, colors = await build_data_for_filters(
        manager, collection=collection, category=category
    )
    main_images = build_main_images(tiles)
    product_manager = ProductImagesManager()
    for k in main_images:
        main_images[k] = product_manager.get_product_catalog_image_path(main_images[k])

    tiles = [map_to_tile_domain(**tile) for tile in tiles]
    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await get_categories_for_items(manager)
    path_to_catalog = f"/catalog/{category}/products"
    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "tiles": tiles,
            "colors": colors,
            "sizes": sizes,
            "page": page,
            "path_to_catalog": path_to_catalog,
            "total_pages": total_pages,
            "total_count": total_count,
            "main_images": main_images,
            "categories": categories,
            "active_tab": "None",
        },
    )
