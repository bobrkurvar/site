from pydantic import BaseModel

class TileInput(BaseModel):
    id: int | None
    name: str
    price: float
    descriptions: str | None