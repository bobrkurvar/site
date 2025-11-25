class TileSize:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width

    def __str__(self):
        return f"{self.height} x {self.width}"


class TileColorFeature:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"


class TileColor:
    def __init__(self, name: str, feature: TileColorFeature):
        self.name = name
        self.feature = feature

    def __str__(self):
        return f"{self.name} {str(self.feature)}"


class TileSurface:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"


class TileMaterial:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"


class Producer:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"


class BoxWeight:

    def __init__(self, weight: float):
        self.weight = weight


class PalletWeight:

    def __init__(self, weight: float):
        self.weight = weight


class Tile:
    def __init__(
        self,
        size: TileSize,
        color: TileColor,
        name: str,
        surface: TileSurface,
        material: TileMaterial,
        box_weight: BoxWeight,
        pallet_weight: PalletWeight,
        producer: Producer,
        tile_id: int | None = None,
    ):
        self.name = name
        self.color = color
        self.size = size
        self.surface = surface
        self.material = material
        self.box_weight = box_weight
        self.pallet_weight = pallet_weight
        self.producer = producer
        self.article = tile_id

    @property
    def present(self):
        return f"{str(self.material)} {self.name} {str(self.size)} {str(self.color)} {str(self.surface)} ({self.article})"

    def __str__(self):
        return f"{str(self.color)} {str(self.surface)} {self.name}"


def map_to_tile_domain(tile_dict: dict) -> Tile:
    size = TileSize(height=tile_dict["size_height"], width=tile_dict["size_width"])
    color_feature = TileColorFeature(name=tile_dict.get("color_feature"))
    color = TileColor(name=tile_dict["color_name"], feature=color_feature)
    surface = TileSurface(name=tile_dict["surface_name"])
    material = TileMaterial(name=tile_dict["material_name"])
    producer = Producer(name=tile_dict["producer_name"])
    box_weight = BoxWeight(weight=tile_dict["box_weight"])
    pallet_weight = PalletWeight(weight=tile_dict["pallet_weight"])


    return Tile(
        size=size,
        color=color,
        name=tile_dict["name"],
        surface=surface,
        material=material,
        box_weight=box_weight,
        pallet_weight=pallet_weight,
        producer=producer,
        tile_id=tile_dict.get("tile_id"),
    )