from fastapi import APIRouter, Depends, File, UploadFile, Form
from repo import get_db_manager, Crud
from typing import Annotated
from domain.tile import Tile
from services.tile import add_tile

router = APIRouter()
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.post("/tile")
async def create_tile(
        name: Annotated[str, Form()],
        price: Annotated[float, Form()],
        image: Annotated[UploadFile, File()],
        manager: dbManagerDep,
):
    result = await add_tile(name, price, image, manager)
    return result

@router.get("/tile")
async def get_tile_lst(manager: dbManagerDep):
    result = await manager.read(Tile)
    return result

@router.get("/tile{id_}")
async def get_tile_by_id(id_: int,  manager: dbManagerDep):
    result = await manager.read(Tile, ident_val=id_)
    return result