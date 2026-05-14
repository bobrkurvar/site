import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from adapters.deps import DbManagerDep
from domain import TileSurface

router = APIRouter(prefix="/admin/tiles/surfaces")
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_delete_surface(
    manager: DbManagerDep,
    name: Annotated[str, Form()] = None,
):
    filters = {}
    if name is not None:
        filters["name"] = name

    await manager.delete(TileSurface, **filters)
    return RedirectResponse("/admin", status_code=303)
