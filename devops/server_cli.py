from .scenarios import (
    deploy,
    migrate,
    generate_miniatures,
    rename_collections,
    prod_env,
    interactive,
)
from .utils import put_compose


TREE = put_compose(
    prod_env,
    generate_miniatures=generate_miniatures,
    rename_collections=rename_collections,
    deploy=deploy,
    migrate=migrate,
    interactive=interactive,
)