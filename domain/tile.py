from decimal import Decimal


class TileSize:
    def __init__(self, width: Decimal, length: Decimal, height: Decimal, size_id: int | None = None):
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
    def __init__(self, color_name: str, feature_name: str = ""):
        self.color_name = color_name
        self.feature_name = feature_name

    def __str__(self):
        return f"{self.color_name} {self.feature_name}"


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


class Category:

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name



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
        category_name: Category,
        surface: TileSurface | None = None,
    ):
        self.id = article
        self.article = article
        self.name = name
        self.color = color
        self.size = size
        self.surface = surface
        self.box = box
        self.boxes_count = boxes_count
        self.producer = producer
        self.category = category_name

    @property
    def present(self):
        return (
            f"{self.category} {self.name} {self.size} {self.color} {self.surface or ''}"
        )

    def __str__(self):
        return f"{self.article} {str(self.color)} {self.surface} {self.name}"

    def to_dict(self):
        return {
            "id": self.article,
            "name": self.name,
            "boxes_count": self.boxes_count,
            "category_name": self.category.name,
            "producer_name": self.producer.name,
            "surface_name": self.surface.name if self.surface else None,
            "size_length": self.size.length,
            "size_width": self.size.width,
            "size_height": self.size.height,
            "size_id": self.size.id,
            "box_area": self.box.area,
            "box_weight": self.box.weight,
            "box_id": self.box.id,
            "color_name": self.color.color_name,
            "feature_name": self.color.feature_name
        }



class TileImage:

    def __init__(self, image: bytes, tile_id: int, image_id: int | None = None):
        self.id = image_id
        self.tile_id = tile_id
        self.image = image


class Collection:
    def __init__(
        self,
        name: str,
        image_bytes: bytes,
        image_path: str | None = None,
        categories: list[Category] | Category | None = None,
        collection_id: int | None = None
    ):
        self.id = collection_id
        self.name = name.strip()
        self.image_path = image_path
        self.image_bytes = image_bytes

        if isinstance(categories, list):
            self.categories = categories
        elif categories:
            self.categories = [categories]
        else:
            self.categories = []

    def add_category(self, category: Category):
        if category not in self.categories:
            self.categories.append(category)


class CollectionCategory:
    def __init__(self, collection_id: int, category_name: str):
        self.collection_id = collection_id
        self.category_name = category_name


def map_to_tile_domain(**tile_dict) -> Tile:
    size = TileSize(
        size_id=tile_dict["size_id"],
        height=tile_dict["size_height"],
        width=tile_dict["size_width"],
        length=tile_dict["size_length"],
    )
    color = TileColor(
        color_name=tile_dict["color_name"], feature_name=tile_dict["feature_name"]
    )
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
    category_name = Category(name=tile_dict["category_name"])

    return Tile(
        size=size,
        color=color,
        name=tile_dict["name"],
        surface=surface,
        box=box,
        boxes_count=tile_dict["boxes_count"],
        producer=producer,
        category_name=category_name,
        article=tile_dict["id"],
    )
