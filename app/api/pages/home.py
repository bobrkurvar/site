from fastapi import APIRouter, Request
from . import templates

router = APIRouter()

@router.get('/')
async def get_main_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})