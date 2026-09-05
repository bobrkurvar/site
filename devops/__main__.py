import sys
from devops.cli import resolve, TREE, select

def main():
    path = tuple(sys.argv[1:])
    node, args = resolve(TREE, path)

    if isinstance(node, dict):
        node = select(node)

    return node(*args)

if __name__ == "__main__":
    main()