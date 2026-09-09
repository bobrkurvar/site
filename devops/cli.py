from collections.abc import Callable
from .scenarios import integration_tests, unit_tests, all_tests, e2e_tests, local_deploy, create_migration, migrate

import questionary


Command = Callable[[], object]
Tree = dict[str, "Tree | Command"]


TREE: Tree = {
    "tests": {
        "unit": unit_tests,
        "integration": integration_tests,
        "e2e": e2e_tests,
        "all": all_tests,
    },
    "local": local_deploy,
    "create_migration": create_migration,
    "migrate": migrate
}


def resolve(tree: Tree, path: tuple[str, ...]):
    node = tree

    for index, name in enumerate(path):
        if not isinstance(node, dict):
            return node, path[index:]

        if name not in node:
            available = ", ".join(node)
            raise ValueError(
                f"Unknown command {name!r}. Available: {available}"
            )

        node = node[name]

    return node, ()



def select(node: Tree) -> Command:
    while isinstance(node, dict):
        choice = questionary.select(
            "Select command:",
            choices=list(node),
        ).ask()

        if choice is None:
            raise KeyboardInterrupt

        node = node[choice]

    return node
