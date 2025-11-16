from pydantic import BaseModel, Field


class TileSizeInput(BaseModel):
    height: float = Field(gt=0)
    width: float = Field(gt=0)

class TileInput(BaseModel):
    id: int | None
    name: str
    descriptions: str | None
    size: TileSizeInput


class TileDelete(BaseModel):
    name: str = None
    size: TileSizeInput = None