from alembic import command
from alembic.config import Config
from core import conf

alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", conf.test_db_url)
command.upgrade(alembic_cfg, "head")
