class TileSize:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width


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


class Surface:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"


class Tile:
    def __init__(
        self,
        size: TileSize,
        color: TileColor,
        name: str,
        surface: Surface,
        tile_id: int | None = None,
    ):
        self.name = name
        self.color = color
        self.size = size
        self.surface = surface
        self.id = tile_id

    def __str__(self):
        return f"{str(self.color)} {str(self.surface)} {self.name}"


class Box:
    def __init__(self, tiles: list[Tile], weight: float):
        self.count = len(tiles)
        self.area = sum(tile.size.height * tile.size.width for tile in tiles)
        self.weight = weight


class Pallet:
    def __init__(self, boxes: list[Box]):
        self.weight = sum(box.weight for box in boxes)
        self.area = sum(box.area for box in boxes)
