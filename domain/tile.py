class TileSize:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width

    def __str__(self):
        return f'{self.height} x {self.width}'


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
        return f'{self.name}'

class Producer:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'{self.name}'

class Tile:
    def __init__(
        self,
        size: TileSize,
        color: TileColor,
        name: str,
        surface: TileSurface,
        material: TileMaterial,
        box_weight: float,
        box_area: float,
        pallet_weight: float,
        pallet_area: float,
        producer: Producer,
        tile_id: int | None = None,
    ):
        self.name = name
        self.color = color
        self.size = size
        self.surface = surface
        self.material = material
        self.box_weight = box_weight
        self.box_area = box_area
        self.pallet_weight = pallet_weight
        self.pallet_area = pallet_area
        self.producer = producer
        self.article = tile_id

    @property
    def present(self):
        return f'{str(self.material)} {self.name} {str(self.size)} {str(self.color)} {str(self.surface)} ({self.article})'

    def __str__(self):
        return f"{str(self.color)} {str(self.surface)} {self.name}"
