from .scenarios import (
    integration_tests,
    unit_tests,
    all_tests,
    e2e_tests,
    deploy,
    create_migration,
    migrate,
    generate_miniatures,
    rename_collections,
    local_env,
    prod_env,
    interactive,
)
from .upload_to_server import upload_release
from .utils import put_compose


TREE = {
    "tests": {
        "unit": unit_tests,
        "integration": integration_tests,
        "e2e": e2e_tests,
        "all": all_tests,
    },

    "local": {
        **put_compose(
            compose=local_env,
            migrate=migrate,
            generate_miniatures=generate_miniatures,
            deploy=deploy,
            interactive=interactive,
        ),
        "create_migration": create_migration,
    },

    "prod": put_compose(
        prod_env,
        generate_miniatures=generate_miniatures,
        rename_collections=rename_collections,
        deploy=deploy,
        migrate=migrate,
        interactive=interactive,
    ),

    "upload_release": upload_release,
}