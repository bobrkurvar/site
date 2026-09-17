import questionary
from collections.abc import Callable


Command = Callable[..., object]
Tree = dict[str, "Tree | Command"]


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