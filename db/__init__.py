from .crud import Crud
from core import config
from .models import *

def get_db_manager() -> Crud:
    db_host = config.db_url
    return Crud(db_host)