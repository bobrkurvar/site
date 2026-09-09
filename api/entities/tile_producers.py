import logging
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from adapters.deps import UowDep
from domain import Producer

router = APIRouter(prefix="/admin/tiles/producers")
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_delete_producer(
    uow: UowDep,
    name: Annotated[str, Form()] = None,
):
    filters = {}
    if name is not None:
        filters["name"] = name
    async with uow:
        await uow.db.delete(Producer, **filters)
    return RedirectResponse("/admin", status_code=303)
