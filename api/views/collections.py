import logging

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from adapters.deps import DbManagerDep, QueryServiceDep
from adapters.images import CollectionImagesManager, ProductImagesManager
from core.config import COLLECTIONS_PER_PAGE
from domain import Collection, CollectionCategory, DomainFilter, Slug
from services.views import (build_tile_filters,
                            fetch_collections_items, get_categories_for_items)
import asyncio

router = APIRouter(tags=["presentation"], prefix="/catalog")
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("/{category}/collections")
async def get_collections_page(
    request: Request,
    manager: DbManagerDep,
    category: str,
    page: int = 1,
):
    limit = COLLECTIONS_PER_PAGE
    offset = (page - 1) * limit
    log.debug("category: %s", category)
    category_name = (await manager.read_one(Slug, slug=category)).name
    category_collections = await manager.read(
        Collection,
        domain_filters=[
            DomainFilter(
                model=CollectionCategory, field="category_name", value=category_name
            )
        ],
        offset=offset,
        limit=limit,
    )
    collections = []
    collection_names = [coll.name for coll in category_collections]
    slugs = await manager.read(Slug, name=collection_names)
    slug_map = {s.name: s.slug for s in slugs}
    collection_manager = CollectionImagesManager()
    for coll in category_collections:
        new_image_path = await collection_manager.get_collections_image_path(
            coll.image_path
        )
        coll.assign_image_path(new_image_path)
        coll.slug = slug_map.get(coll.name)
        collections.append(coll)
    total_count = await manager.count(CollectionCategory, category_name=category_name)
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
    manager: DbManagerDep,
    query_service: QueryServiceDep,
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

    filters = await query_service.get_catalog_filters(
        collection_slug=collection, category_slug=category
    )
    #main_images = build_main_images(tiles)
    product_manager = ProductImagesManager()
    # for k in main_images:
    #     main_images[k] = await product_manager.get_product_catalog_image_path(
    #         main_images[k]
    #     )
    for tile in tiles:
        coroutines = (
            product_manager.get_product_catalog_image_path(path)
            for path in tile.images_paths
        )
        resolved_paths = await asyncio.gather(*coroutines)
        tile.set_images(resolved_paths)

    total_pages = max((total_count + limit - 1) // limit, 1)
    categories = await get_categories_for_items(manager)
    path_to_catalog = f"/catalog/{category}/products"
    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "tiles": tiles,
            "page": page,
            "path_to_catalog": path_to_catalog,
            "total_pages": total_pages,
            "total_count": total_count,
            #"main_images": main_images,
            "categories": categories,
            "filters": filters,
            "active_tab": "None",
        },
    )
