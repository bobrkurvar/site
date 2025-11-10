from fastapi import APIRouter, Depends
from db import get_db_manager
from typing import Annotated
from db import Crud
from db import Catalog
from .schemas.tile import TileInput

router = APIRouter()
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.post("/tile")
async def create_tile(tile: TileInput, manager: dbManagerDep):
    result = await manager.create(model=Catalog, **tile.model_dump())
    return result

@router.get("/tile")
async def get_tile_lst(manager: dbManagerDep):
    result = await manager.read(model=Catalog)
    return result

@router.get("/tile{id_}")
async def get_tile_by_id(id_: int, manager: dbManagerDep):
    result = await manager.read(model=Catalog, ident_val=id_)
    return result