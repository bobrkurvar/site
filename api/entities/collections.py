import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from adapters.deps import DbManagerDep, HttpClientDep
from adapters.images import CollectionImagesManager, ImageGenerator
from services.collections import add_collection, delete_collection
from domain import Collection, Category

router = APIRouter(prefix="/admin/tiles/collections")
log = logging.getLogger(__name__)


@router.post("/create")
async def admin_create_tile_collection(
    manager: DbManagerDep,
    http_client: HttpClientDep,
    collection_name: Annotated[str, Form()],
    category_name: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
):
    image = await image.read()
    collection = Collection(name=collection_name, category=Category(category_name), image_bytes=image)
    await add_collection(
        # collection_name,
        # image,
        # category_name,
        collection,
        manager,
        images_generator=ImageGenerator(http_client),
        file_manager=CollectionImagesManager(),
    )
    return RedirectResponse("/admin", status_code=303)


@router.post("/delete")
async def admin_delete_tile_collections(
    manager: DbManagerDep,
    collection_name: Annotated[str, Form()],
):
    collection_name = collection_name.strip()
    await delete_collection(
        collection_name=collection_name,
        manager=manager,
        file_manager=CollectionImagesManager(),
    )
    return RedirectResponse("/admin", status_code=303)
