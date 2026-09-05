import sys
from devops.cli import resolve, TREE, select

def main():
    path = tuple(sys.argv[1:])
    node = resolve(TREE, path)

    if isinstance(node, dict):
        node = select(node)

    return node()

if __name__ == "__main__":
    main()