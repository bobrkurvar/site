import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from domain import TileSurface
from repo import Crud, get_db_manager

router = APIRouter(prefix="/admin/tiles")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/surface/create")
async def admin_create_surface(manager: dbManagerDep, name: Annotated[str, Form()]):
    await manager.create(TileSurface, name=name)
    return RedirectResponse("/admin", status_code=303)


@router.post("/surface/delete")
async def admin_delete_all_colors(manager: dbManagerDep):
    await manager.delete(TileSurface)
    return RedirectResponse("/admin", status_code=303)


@router.post("/surface/{name}")
async def admin_delete_color(name: str, manager: dbManagerDep):
    await manager.delete(TileSurface, name=name)
    return RedirectResponse("/admin", status_code=303)
