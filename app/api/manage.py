from fastapi import APIRouter, Depends, File, UploadFile
from db import get_db_manager
from typing import Annotated
from db import Crud
from db import Catalog
from .schemas.tile import TileInput
from pathlib import Path

router = APIRouter()
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


@router.post("/tile")
async def create_tile(tile: TileInput, manager: dbManagerDep):
    upload_dir = Path("static/uploads")
    file_path = upload_dir / tile.name
    result = await manager.create(model=Catalog, **tile.model_dump(), image_path=str(file_path))
    return result

@router.post("/tile/{tile_id}/image")
async def load_tile_image(tile_id: int, image: Annotated[UploadFile, File()], manager: dbManagerDep):
    tile = await manager.read(model=Catalog, ident_val=tile_id)
    file_path = tile.get('image_path')
    with open(file_path, "wb") as fw:
        fw.write(await image.read())

@router.get("/tile")
async def get_tile_lst(manager: dbManagerDep):
    result = await manager.read(model=Catalog)
    return result

@router.get("/tile{id_}")
async def get_tile_by_id(id_: int,  manager: dbManagerDep):
    result = await manager.read(model=Catalog, ident_val=id_)
    return result