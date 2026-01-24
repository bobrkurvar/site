import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from domain import TileSurface
from adapters.repo import Crud, get_db_manager

router = APIRouter(prefix="/admin/tiles/surfaces")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_create_tile_box(
    manager: dbManagerDep,
    name: Annotated[str, Form()] = None,
):
    filters = {}
    if name is not None:
        filters["name"] = name

    await manager.delete(TileSurface, **filters)
    return RedirectResponse("/admin", status_code=303)
