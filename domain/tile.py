from decimal import Decimal


class TileSize:
    def __init__(self, height: Decimal, width: Decimal):
        self.height = height
        self.width = width

    def __str__(self):
        return f"{self.height} × {self.width}(мм)"


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

    def __init__(self, weight: Decimal, area: Decimal):
        self.weight = weight
        self.area = area

    def __str__(self):
        return str(self.weight)


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

    @property
    def present(self):
        return f"{self.name} {self.size} {self.color} {self.surface or ''} ({self.article})"

    def __str__(self):
        return f"{self.article} {str(self.color)} {str(self.surface)} {self.name}"

class TileImages:

    def __init__(self, images: list[bytes]):
        self.images = images


def map_to_tile_domain(tile_dict: dict) -> Tile:
    size = TileSize(height=tile_dict["size_height"], width=tile_dict["size_width"])
    color = TileColor(name=tile_dict["color_name"], feature=tile_dict["feature_name"])
    surface = TileSurface(name=tile_dict["surface_name"]) if tile_dict["surface_name"] else None
    producer = Producer(name=tile_dict["producer_name"])
    box = Box(weight=tile_dict["box_weight"], area=tile_dict["box_area"])

    return Tile(
        size=size,
        color=color,
        name=tile_dict["name"],
        surface=surface,
        box=box,
        boxes_count = tile_dict['boxes_count'],
        producer=producer,
        article=tile_dict["id"],
    )
