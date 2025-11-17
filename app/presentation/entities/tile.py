import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from repo import Crud, get_db_manager
from services.tile import add_tile, delete_tile

router = APIRouter()
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/delete-all")
async def delete_tile_by_criteria_or_all(
    manager: dbManagerDep,
):
    await delete_tile(manager)
    return RedirectResponse("/admin", status_code=303)


@router.post("/delete/{tile_id}")
async def admin_delete_tile(tile_id: int, manager: dbManagerDep):
    await delete_tile(manager, id=tile_id)
    return RedirectResponse("/admin", status_code=303)


@router.post("/create")
async def admin_create_tile(
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color: Annotated[str, Form()],
    surface: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
    manager: dbManagerDep,
):
    bytes_image = await image.read()
    height_str, width_str = size.split(",")
    height = float(height_str)
    width = float(width_str)
    log.debug("height: %s, width: %s, color: %s, surface: %s", height, width, color, surface)
    await add_tile(name, height, width, color, surface, bytes_image, manager)
    return RedirectResponse("/admin", status_code=303)
