from collections.abc import Callable
from .scenarios import integration_tests, unit_tests

import questionary


Command = Callable[[], object]
Tree = dict[str, "Tree | Command"]


TREE: Tree = {
    "tests": {
        "integration": integration_tests,
        "unit": unit_tests,
    },
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


# def select(node: Tree) -> Command:
#     while isinstance(node, dict):
#         names = tuple(node)
#
#         for i, name in enumerate(names, 1):
#             print(f"{i}. {name}")
#
#         choice = input("> ").strip()
#
#         if choice.isdigit():
#             index = int(choice) - 1
#
#             if 0 <= index < len(names):
#                 choice = names[index]
#
#         if choice not in node:
#             print("Unknown command")
#             continue
#
#         node = node[choice]
#
#     return node


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
