from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_validator

class CreateTile(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str
    size: str
    color_name: str
    producer_name: str
    box_weight: Decimal
    box_area: Decimal
    boxes_count: int
    category_name: str
    feature_name: str | None = None
    surface_name: str = ""

    @property
    def length(self) -> Decimal:
        return Decimal(self.size.split()[0])

    @property
    def width(self) -> Decimal:
        return Decimal(self.size.split()[1])

    @property
    def height(self) -> Decimal:
        return Decimal(self.size.split()[2])

    @field_validator("feature_name")
    @classmethod
    def empty_str_to_none(cls, v: str | None) -> str | None:
        if v == "":
            return None
        return v

