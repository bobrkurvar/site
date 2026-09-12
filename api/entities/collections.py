import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from adapters.deps import UowDep, ImageHttpClientDep
from adapters.images import CollectionImagesManager
from domain import Category, Collection, Image
from services.collections import add_collection, delete_collection

router = APIRouter(prefix="/admin/tiles/collections")
log = logging.getLogger(__name__)


@router.post("/create")
async def admin_create_collection(
    uow: UowDep,
    images_generator: ImageHttpClientDep,
    collection_name: Annotated[str, Form()],
    category_name: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
):
    image = await image.read()
    collection = Collection(
        name=collection_name,
        categories=Category(category_name),
        image=Image(image_bytes=image),
    )
    await add_collection(
        collection=collection,
        uow=uow,
        images_generator=images_generator,
        file_manager=CollectionImagesManager(),
    )
    return RedirectResponse("/admin", status_code=303)


@router.post("/delete")
async def admin_delete_collections(
    uow: UowDep,
    collection_name: Annotated[str, Form()],
):
    collection_name = collection_name.strip()
    await delete_collection(
        collection_name=collection_name,
        uow=uow,
        file_manager=CollectionImagesManager(),
    )
    return RedirectResponse("/admin", status_code=303)
