class TileSize:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width


class TileColorFeature:
    def __init__(self, name: str):
        self.name = name


class TileColor:
    def __init__(self, name: str, feature: TileColorFeature):
        self.name = name
        self.feature = feature


class Tile:
    def __init__(
        self, size: TileSize, color: TileColor, name: str, tile_id: int | None = None
    ):
        self.name = name
        self.color = color
        self.size = size
        self.id = tile_id


class Box:
    def __init__(self, count: int, area: float, weight: float):
        self.count = count
        self.area = area
        self.weight = weight


class Pallet:
    def __init__(self, weight: float, area: float):
        self.weight = weight
        self.area = area


class Surface:
    def __init__(self, name: str):
        self.name = name
