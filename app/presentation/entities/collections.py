import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, File, UploadFile
from fastapi.responses import RedirectResponse

from domain import Collections
from repo import Crud, get_db_manager
from services.collections import add_collection

router = APIRouter(prefix="/admin/tiles/collections")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/create")
async def admin_create_tile_box(
        manager: dbManagerDep,
        name: Annotated[str, Form()],
        category: Annotated[str, Form()],
        image: Annotated[UploadFile, File()]
):
    image = await image.read()
    await add_collection(name, category, image, manager)
    return RedirectResponse("/admin", status_code=303)

@router.post("/delete")
async def admin_create_tile_box(manager: dbManagerDep, name: Annotated[str, Form()] = None):
    if name:
        await manager.delete(Collections, name=name)
    else:
        await manager.delete(Collections)
    return RedirectResponse("/admin", status_code=303)
