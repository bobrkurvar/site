from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from repo import get_db_manager, Crud
from typing import Annotated
from services.tile import add_tile, delete_tile
import logging

router = APIRouter()
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post('/tile/delete-all')
async def delete_tile_by_criteria_or_all(
        manager: dbManagerDep,
):
    await delete_tile(manager)
    return RedirectResponse("/admin", status_code=303)


@router.post("/tile/delete/{tile_id}")
async def admin_delete_tile(tile_id: int, manager: dbManagerDep):
    await delete_tile(manager, id=tile_id)
    return RedirectResponse("/admin", status_code=303)


@router.post("/tile")
async def admin_create_tile(
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
    manager: dbManagerDep,
):
    bytes_image = await image.read()
    height_str, width_str = size.split(',')
    height = float(height_str)
    width = float(width_str)
    await add_tile(name, height, width, color, bytes_image, manager)
    return RedirectResponse("/admin", status_code=303)
