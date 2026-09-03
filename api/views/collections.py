import logging

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from adapters.deps import UowDep, QueryServiceDep
from adapters.images import CollectionImagesManager, ProductImagesManager
from core.config import COLLECTIONS_PER_PAGE
from domain import Collection, CollectionCategory, DomainFilter, Category
from services.views import (
    build_tile_filters,
    fetch_collections_items,
    get_categories_for_items,
)
import asyncio

router = APIRouter(tags=["presentation"], prefix="/catalog")
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("/{category_slug}/{category_id:int}/collections")
async def get_collections_page(
    request: Request,
    uow: UowDep,
    category_slug: str,
    category_id: int,
    page: int = 1,
):
    limit = COLLECTIONS_PER_PAGE
    offset = (page - 1) * limit
    async with uow:
        category = await uow.db.read_one(Category, id=category_id, with_raise=True)
        category_name = category.name
        category_collections = await uow.db.read(
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
        collection_manager = CollectionImagesManager()
        for coll in category_collections:
            new_image_path = await collection_manager.get_collections_image_path(
                coll.image_path
            )
            coll.assign_image_path(new_image_path)
            collections.append(coll)
        total_count = await uow.db.count(
            CollectionCategory, category_name=category_name
        )
        total_pages = max((total_count + limit - 1) // limit, 1)
        categories = await get_categories_for_items(uow.db)

    category_path = f"{category_slug}/{category_id}"
    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "collections": collections,
            "total_pages": total_pages,
            "categories": categories,
            "page": page,
            "active_tab": "collections",
            "category_path": category_path,
        },
    )


@router.get(
    "/{category_slug}/{category_id:int}/collections/{collection_slug}/{collection_id:int}"
)
async def get_catalog_tiles_page(
    request: Request,
    uow: UowDep,
    query_service: QueryServiceDep,
    collection_slug: str,
    collection_id: int,
    category_slug: str,
    category_id: int,
    producer: str | None = None,
    size: str | None = None,
    color: str | None = None,
    page: int = 1,
):
    limit = COLLECTIONS_PER_PAGE
    offset = (page - 1) * limit
    async with uow:
        category = await uow.db.read_one(
            Category,
            id=category_id,
            with_raise=True,
        )

        collection = await uow.db.read_one(
            Collection,
            id=collection_id,
            with_raise=True,
        )

        # Проверяем, что эта коллекция действительно открыта внутри этой категории
        await uow.db.read_one(
            CollectionCategory,
            collection_id=collection_id,
            category_name=category.name,
            with_raise=True,
        )

        filters = await build_tile_filters(uow.db, producer, size, color, category.name)

        tiles, total_count = await fetch_collections_items(
            uow.db, collection.name, limit, offset, **filters
        )

        filter_options = await query_service.get_catalog_filters(
            collection_name=collection.name, category_name=category.name
        )

        product_manager = ProductImagesManager()
        for tile in tiles:
            coroutines = (
                product_manager.get_product_catalog_image_path(path)
                for path in tile.images_paths
            )
            resolved_paths = await asyncio.gather(*coroutines)
            tile.set_images(resolved_paths)

        total_pages = max((total_count + limit - 1) // limit, 1)
        categories = await get_categories_for_items(uow.db)

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "tiles": tiles,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "categories": categories,
            "filters": filter_options,
            "active_tab": "None",
        },
    )
