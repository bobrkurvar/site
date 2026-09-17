import sys

from devops.cli_common import resolve, select
from devops.server_cli import TREE


def main():
    path = tuple(sys.argv[1:])
    node, args = resolve(TREE, path)

    if isinstance(node, dict):
        node = select(node)

    return node(*args)


if __name__ == "__main__":
    main()