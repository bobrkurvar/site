from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from repo import get_db_manager, Crud
from typing import Annotated
from domain import TileColor
import logging

router = APIRouter()
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post('/tile/color')
async def admin_create_tile_color(manager: dbManagerDep, name: Annotated[str, Form()], feature: Annotated[str, Form()]):
    await manager.create(TileColor, name=name, fature=feature)
    return RedirectResponse("/admin", status_code=303)


@router.post('tile/color/delete')
async def admin_delete_all_colors(manager: dbManagerDep):
    await manager.delete(TileColor)
    return RedirectResponse("/admin", status_code=303)

@router.post('tile/color/delete/{name}')
async def admin_delete_all_colors(name: str, manager: dbManagerDep):
    await manager.delete(TileColor, name=name)
    return RedirectResponse("/admin", status_code=303)
