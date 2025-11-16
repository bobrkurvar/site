from repo.crud import Crud
from db.models import Catalog, SizeTile
from domain.tile import Tile
from domain.tile_size import TileSize
from core import config

def get_db_manager() -> Crud:
    db_host = config.db_url
    manager = Crud(db_host)

    manager.register(Tile, Catalog)
    manager.register(TileSize, SizeTile)

    return manager