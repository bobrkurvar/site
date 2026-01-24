import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain import Categories, Tile
from adapters.repo import Crud, get_db_manager

router = APIRouter()
templates = Jinja2Templates("templates")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]

log = logging.getLogger(__name__)


@router.get("/")
async def get_main_page(request: Request, manager: dbManagerDep):
    slides_dir = Path('static/images/slides')

    slide_images = [
        f"/static/images/slides/{img.name}"
        for img in slides_dir.iterdir()
        if img.is_file()
    ]
    categories = await manager.read(Tile, distinct="category_name")
    categories = [Categories(name=category["category_name"]) for category in categories]

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "slide_images": slide_images,
            "categories": categories,
        },
    )
