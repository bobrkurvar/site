import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from adapters.crud import Crud, get_db_manager
from adapters.images import (CollectionImagesManager,
                             generate_image_collections_catalog)
from services.collections import add_collection, delete_collection

router = APIRouter(prefix="/admin/tiles/collections")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/create")
async def admin_create_tile_collection(
    manager: dbManagerDep,
    collection_name: Annotated[str, Form()],
    category_name: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
):
    collection_name = collection_name.strip()
    category_name = category_name.strip()
    image = await image.read()
    await add_collection(
        collection_name,
        image,
        category_name,
        manager,
        generate_images=generate_image_collections_catalog,
        file_manager=CollectionImagesManager(),
    )
    return RedirectResponse("/admin", status_code=303)


@router.post("/delete")
async def admin_delete_tile_collections(
    manager: dbManagerDep,
    collection_name: Annotated[str, Form()],
    category_name: Annotated[str, Form()],
):
    collection_name = collection_name.strip()
    category_name = category_name.strip()
    await delete_collection(
        collection_name=collection_name,
        manager=manager,
        category_name=category_name,
        file_manager=CollectionImagesManager(),
    )
    return RedirectResponse("/admin", status_code=303)
