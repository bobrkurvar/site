from pydantic import BaseModel, Field


class TileSizeInput(BaseModel):
    height: float = Field(gt=0)
    width: float = Field(gt=0)


class TileDelete(BaseModel):
    name: str = None
    size: TileSizeInput = None
