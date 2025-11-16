import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from app.schemas.tile import TileSizeInput
from domain import TileSize
from repo import Crud, get_db_manager

router = APIRouter()
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/tile/sizes/delete")
async def admin_delete_tile_size(
    manager: dbManagerDep,
    height: Annotated[float | None, Form(gt=0)] = None,
    width: Annotated[float | None, Form(gt=0)] = None,
):
    if height is not None and width is not None:
        await manager.delete(TileSize, height=height, width=width)
    else:
        await manager.delete(TileSize)
    return RedirectResponse("/admin", status_code=303)


@router.post("/tile/sizes")
async def admin_create_tile_size(
    manager: dbManagerDep,
    height: Annotated[float | None, Form(gt=0)],
    width: Annotated[float | None, Form(gt=0)],
):
    await manager.create(TileSize, height=height, width=width)
    return RedirectResponse("/admin", status_code=303)


@router.post("/tile/sizes/delete")
async def admin_delete_tile_size(tile_size: TileSizeInput, manager: dbManagerDep):
    await manager.delete(TileSize, **tile_size.model_dump())
    return RedirectResponse("/admin", status_code=303)
