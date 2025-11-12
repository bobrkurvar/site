
class Tile:

    def __init__(self, price: float, name: str, image_path: str, tile_id: int | None = None):
        self.price = price
        self.name = name
        self.image_path = image_path
        self.id = tile_id
        
