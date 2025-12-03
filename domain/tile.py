from decimal import Decimal

from slugify import slugify


class TileSize:
    def __init__(self, size_id: int, width: Decimal, length: Decimal, height: Decimal):
        self.id = size_id
        self.height = height
        self.width = width
        self.length = length

    def __str__(self):
        return f"{self.format_decimal(self.length)}×{self.format_decimal(self.width)}×{self.format_decimal(self.height)}"

    @staticmethod
    def format_decimal(value: Decimal) -> str:
        as_float = float(value)
        if as_float.is_integer():
            return str(int(as_float))
        return f"{as_float:g}"


class TileColor:
    def __init__(self, name: str, feature: str = ""):
        self.name = name
        self.feature = feature

    def __str__(self):
        return f"{self.name} {self.feature}"


class TileSurface:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"


class Producer:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"


class Box:

    def __init__(self, box_id: int, weight: Decimal, area: Decimal):
        self.id = box_id
        self.weight = weight
        self.area = area

    def __str__(self):
        return str(self.weight.normalize())


class Types:

    _slug_to_name = {}

    def __init__(self, name: str):
        self.name = name
        self.slug = slugify(name)
        self.__class__._slug_to_name[self.slug] = name

    def __str__(self):
        return self.name

    @classmethod
    def get_category_from_slug(cls, slug: str):
        return cls._slug_to_name[slug]


class Tile:
    def __init__(
        self,
        size: TileSize,
        color: TileColor,
        name: str,
        box: Box,
        boxes_count: int,
        producer: Producer,
        article: int,
        tile_type: Types,
        surface: TileSurface | None = None,
    ):
        self.name = name
        self.color = color
        self.size = size
        self.surface = surface
        self.box = box
        self.boxes_count = boxes_count
        self.producer = producer
        self.article = article
        self.tile_type = tile_type

    @property
    def present(self):
        return f"{self.tile_type} {self.name} {self.size} {self.color} {self.surface or ''}"

    @property
    def present_tile_url(self):
        return f"{self.tile_type.slug}"

    def __str__(self):
        return f"{self.article} {str(self.color)} {self.surface} {self.name}"


class TileImages:

    def __init__(self, images: list[bytes]):
        self.images = images


def map_to_tile_domain(tile_dict: dict) -> Tile:
    size = TileSize(
        size_id=tile_dict["id"],
        height=tile_dict["size_height"],
        width=tile_dict["size_width"],
        length=tile_dict["size_length"],
    )
    color = TileColor(name=tile_dict["color_name"], feature=tile_dict["feature_name"])
    surface = (
        TileSurface(name=tile_dict["surface_name"])
        if tile_dict["surface_name"]
        else None
    )
    producer = Producer(name=tile_dict["producer_name"])
    box = Box(
        box_id=tile_dict["box_id"],
        weight=tile_dict["box_weight"],
        area=tile_dict["box_area"],
    )
    tile_type = Types(name=tile_dict["tile_type"])

    return Tile(
        size=size,
        color=color,
        name=tile_dict["name"],
        surface=surface,
        box=box,
        boxes_count=tile_dict["boxes_count"],
        producer=producer,
        tile_type=tile_type,
        article=tile_dict["id"],
    )
