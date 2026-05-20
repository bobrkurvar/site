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
    surface_name: str | None = None
    @property
    def length(self) -> Decimal:
        return Decimal(self.size.split()[0])

    @property
    def width(self) -> Decimal:
        return Decimal(self.size.split()[1])

    @property
    def height(self) -> Decimal:
        return Decimal(self.size.split()[2])

    @field_validator("*")
    @classmethod
    def empty_str_to_none(cls, v: str | None) -> str | None:
        if v == "":
            return None
        return v

class UpdateTile(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    article: int
    name: str | None = None
    size: str | None = None
    color_name: str | None = None
    producer_name: str | None = None
    box_weight: Decimal | None = None
    box_area: Decimal | None = None
    boxes_count: int | None = None
    category_name: str | None = None
    feature_name: str | None = None
    surface_name: str | None = None

    @field_validator('*')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    def custom_dump(self) -> dict:
        try:
            length, width, height = self.size.split()
            size_dict = {
                "length": Decimal(length),
                "width": Decimal(width),
                "height": Decimal(height),
            }
        except ValueError:
            raise ValueError("Size must be in format 'length width height'")

        return {
            "article": self.article,
            "name": self.name,
            "size": size_dict,
            "box": {
                "weight": Decimal(self.box_weight),
                "area": Decimal(self.box_area)
            },
            "color": {
                "color_name": self.color_name,
                "feature_name": self.feature_name
            },
            "producer_name": self.producer_name,
            "category_name": self.category_name,
            "surface_name": self.surface_name,
            "boxes_count": int(self.boxes_count)
        }