from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator
from domain import Collection, Tile
from adapters.images import CollectionImagesManager, ProductImagesManager
from dataclasses import dataclass
from functools import cached_property

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
    def empty_str_to_none(cls, v):
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

    @field_validator("*")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    def custom_dump(self) -> dict:
        result = {"article": self.article}
        if self.name is not None:
            result["name"] = self.name
        if self.producer_name is not None:
            result["producer_name"] = self.producer_name
        if self.category_name is not None:
            result["category_name"] = self.category_name
        if self.surface_name is not None:
            result["surface_name"] = self.surface_name
        if self.boxes_count is not None:
            result["boxes_count"] = self.boxes_count

        if self.size:
            try:
                length, width, height = self.size.split()
                result["size"] = {
                    "length": Decimal(length),
                    "width": Decimal(width),
                    "height": Decimal(height),
                }
            except ValueError:
                raise ValueError("Size must be in format 'length width height'")

        if self.box_weight is not None or self.box_area is not None:
            result["box"] = {"weight": self.box_weight, "area": self.box_area}
        if self.color_name is not None or self.feature_name is not None:
            result["color"] = {
                "color_name": self.color_name,
                "feature_name": self.feature_name,
            }
        return result

@dataclass
class ImageOut:
    image_url: str
    fallback_url: str


@dataclass
class ProductDetailsOut:
    tile: Tile

    @cached_property
    def images(self) -> list[ImageOut]:
        manager = ProductImagesManager()

        return [
            ImageOut(
                image_url="/" + manager.get_product_details_image_path(path),
                fallback_url="/" + path,
            )
            for path in self.tile.images_paths
        ]

    def __getattr__(self, name):
        return getattr(self.tile, name)


# @dataclass
# class ProductDetailsOut:
#     tile: Tile
#
#
#     @property
#     def image_url(self) -> str | None:
#         path = self.tile.main_image_path
#         if not path:
#             return None
#
#         return "/" + ProductImagesManager().get_product_details_image_path(path)
#
#     @property
#     def fallback_url(self) -> str | None:
#         path = self.tile.main_image_path
#         if not path:
#             return None
#
#         return "/" + path
#
#     def __getattr__(self, name):
#         return getattr(self.tile, name)


@dataclass
class ProductCatalogOut:
    tile: Tile

    @property
    def image_url(self) -> str | None:
        path = self.tile.main_image_path
        if not path:
            return None

        return "/" + ProductImagesManager().get_product_catalog_image_path(path)

    @property
    def fallback_url(self) -> str | None:
        path = self.tile.main_image_path
        if not path:
            return None

        return "/" + path

    def __getattr__(self, name):
        return getattr(self.tile, name)


@dataclass
class CollectionCatalogOut:
    collection: Collection

    @property
    def image_url(self) -> str | None:
        if not self.collection.image_path:
            return None

        return "/" + CollectionImagesManager().get_collections_image_path(
            self.collection.image_path
        )

    @property
    def fallback_url(self) -> str | None:
        if not self.collection.image_path:
            return None

        return "/" + self.collection.image_path

    def __getattr__(self, name):
        return getattr(self.collection, name)