from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from db import get_db_manager, Crud
from typing import Annotated
from db import Catalog


router = APIRouter()
templates = Jinja2Templates('templates')
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]

@router.get("/")
async def get_main_page(request: Request, manager: dbManagerDep):
    products = await manager.read(model=Catalog)
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "products": products}
    )
