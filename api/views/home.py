import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from adapters.crud import Crud, get_db_manager
from adapters.images import SlideImagesManager
from services.views import get_categories_for_items

router = APIRouter()
templates = Jinja2Templates("templates")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]

log = logging.getLogger(__name__)


@router.get("/")
async def get_main_page(request: Request, manager: dbManagerDep):
    slide_manager = SlideImagesManager()
    slide_images = slide_manager.get_all_slides_paths
    categories = await get_categories_for_items(manager)
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "slide_images": slide_images,
            "categories": categories,
        },
    )


@router.get("/cookie/delete")
async def cookie_delete(request: Request):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token", path="/")
    # response.delete_cookie("refresh_token", path="/")
    log.debug("COOKIES after delete: %s", request.cookies)
    return response
