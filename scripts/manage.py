import subprocess
import sys

def run(cmd: list[str]) -> int:
    print(">", " ".join(cmd))
    return subprocess.call(cmd)

PROD_PROJECT = "site"
PROD_COMPOSE = "docker-compose.yml"
TEST_PROJECT = "tests"
TEST_COMPOSE = "docker-compose.test.yml"

def test() -> int:
    code = run([
        "docker", "compose", "-p", TEST_PROJECT, "-f", TEST_COMPOSE,
        "up", "--build", "-d", "postgres", "migrate", "runner", "app"
    ])
    if code != 0:
        return code

    code = run([
        "docker", "compose", "-p", TEST_PROJECT, "-f", TEST_COMPOSE,
        "build", "e2e_tests"
    ])
    if code != 0:
        return code

    run([
        "docker", "compose", "-p", TEST_PROJECT, "-f", TEST_COMPOSE,
        "run", "--rm", "--no-deps", "e2e_tests"
    ])

    code = run([
        "docker", "compose", "-p", TEST_PROJECT, "-f", TEST_COMPOSE,
        "build", "int_tests"
    ])
    if code != 0:
        return code

    code = run([
        "docker", "compose", "-p", TEST_PROJECT, "-f", TEST_COMPOSE,
        "run", "--rm", "--no-deps", "int_tests"
    ])

    run(["docker", "compose", "-p", TEST_PROJECT, "-f", TEST_COMPOSE, "down", "-v", "--remove-orphans"])
    return code

def prod() -> int:
    return run([
        "docker", "compose", "-p", PROD_PROJECT, "-f", PROD_COMPOSE,
        "up", "--build"
    ])

def down() -> int:
    return run([
        "docker", "compose", "-p", PROD_PROJECT, "-f", PROD_COMPOSE,
        "down", "--remove-orphans"
    ])

def down_test() -> int:
    return run([
        "docker", "compose", "-p", TEST_COMPOSE, "-f",TEST_COMPOSE,
        "down", "-v", "--remove-orphans"
    ])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [test|prod|down|down-test]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "test":
        code = test()
    elif cmd == "prod":
        code = prod()
    elif cmd == "down":
        code = down()
    elif cmd == "down-test":
        code = down_test()
    else:
        print(f"Unknown command: {cmd}")
        code = 1

    sys.exit(code)