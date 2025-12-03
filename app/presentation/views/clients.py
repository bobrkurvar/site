import logging
from fastapi import APIRouter
from fastapi.responses import RedirectResponse



router = APIRouter()

log = logging.getLogger(__name__)


@router.get("/clients")
async def get_clients_page():
    return RedirectResponse("/", status_code=303)
