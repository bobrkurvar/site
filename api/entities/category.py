import logging
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from adapters.deps import DbManagerDep
from domain import Category

router = APIRouter(prefix="/admin/tiles/categories")
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_delete_category(manager: DbManagerDep, name: Annotated[str, Form()]):
    filters = {}
    if name is not None:
        filters["name"] = name

    await manager.delete(Category, **filters)
    return RedirectResponse("/admin", status_code=303)
