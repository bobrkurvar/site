import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from adapters.images import generate_image_collections_catalog_bg
from adapters.repo import Crud, get_db_manager
from adapters.files import save_files, delete_files
from services.collections import add_collection, delete_collection

router = APIRouter(prefix="/admin/tiles/collections")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/create")
async def admin_create_tile_collection(
    manager: dbManagerDep,
    name: Annotated[str, Form()],
    category_name: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
):
    name = name.strip()
    category_name = category_name.strip()
    image = await image.read()
    await add_collection(name, image, category_name, manager, generate_image_variant_callback=generate_image_collections_catalog_bg, save_files=save_files)
    return RedirectResponse("/admin", status_code=303)


@router.post("/delete")
async def admin_delete_tile_collections(
    manager: dbManagerDep, name: Annotated[str, Form()]
):
    await delete_collection(name, manager, delete_files=delete_files)
    return RedirectResponse("/admin", status_code=303)
