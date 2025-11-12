from repo.crud import Crud
from db.models import Catalog
from domain.tile import Tile
from core import config

def get_db_manager() -> Crud:
    db_host = config.db_url
    manager = Crud(db_host)

    manager.register(Tile, Catalog)

    return manager