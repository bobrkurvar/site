# from collections.abc import Callable
# from .scenarios import integration_tests, unit_tests, all_tests, e2e_tests, deploy, create_migration, migrate, generate_miniatures, rename_collections, local_env, prod_env, interactive
# from .utils import put_compose
# from .upload_to_server import upload_release
# import questionary
#
#
# Command = Callable[[], object]
#
# Tree = dict[str, "Tree | Command"]
# TREE: Tree = {
#     "tests": {
#         "unit": unit_tests,
#         "integration": integration_tests,
#         "e2e": e2e_tests,
#         "all": all_tests,
#     },
#     "local": {
#         **put_compose(
#             compose=local_env,
#             migrate=migrate,
#             generate_miniatures=generate_miniatures,
#             deploy=deploy,
#             interactive=interactive
#         ),
#         "create_migration": create_migration,
#     },
#     "prod": put_compose(
#         prod_env,
#         generate_miniatures=generate_miniatures,
#         rename_collections=rename_collections,
#         deploy=deploy,
#         migrate=migrate,
#         interactive=interactive
#     ),
#     "upload_release": upload_release
# }
#
#
#
# def resolve(tree: Tree, path: tuple[str, ...]):
#     node = tree
#
#     for index, name in enumerate(path):
#         if not isinstance(node, dict):
#             return node, path[index:]
#
#         if name not in node:
#             available = ", ".join(node)
#             raise ValueError(
#                 f"Unknown command {name!r}. Available: {available}"
#             )
#
#         node = node[name]
#
#     return node, ()
#
#
#
# def select(node: Tree) -> Command:
#     while isinstance(node, dict):
#         choice = questionary.select(
#             "Select command:",
#             choices=list(node),
#         ).ask()
#
#         if choice is None:
#             raise KeyboardInterrupt
#
#         node = node[choice]
#
#     return node
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