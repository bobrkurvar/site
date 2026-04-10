import subprocess
import sys

def run(cmd: list[str]) -> int:
    print(">", " ".join(cmd))
    return subprocess.call(cmd)

def test() -> int:
    project = "tests"
    compose = "docker-compose.test.yml"

    code = run([
        "docker", "compose", "-p", project, "-f", compose,
        "up", "--build", "-d", "postgres", "migrate", "runner", "app"
    ])
    if code != 0:
        return code

    code = run([
        "docker", "compose", "-p", project, "-f", compose,
        "build", "e2e_tests"
    ])
    if code != 0:
        return code

    run([
        "docker", "compose", "-p", project, "-f", compose,
        "run", "--rm", "--no-deps", "e2e_tests"
    ])

    code = run([
        "docker", "compose", "-p", project, "-f", compose,
        "build", "int_tests"
    ])
    if code != 0:
        return code

    code = run([
        "docker", "compose", "-p", project, "-f", compose,
        "run", "--rm", "--no-deps", "int_tests"
    ])

    run(["docker", "compose", "-p", project, "-f", compose, "down", "-v", "--remove-orphans"])
    return code

def prod() -> int:
    return run([
        "docker", "compose", "-p", "pysite", "-f", "docker-compose.yml",
        "up", "--build"
    ])

def down() -> int:
    return run([
        "docker", "compose", "-p", "pysite", "-f", "docker-compose.yml",
        "down", "--remove-orphans"
    ])

def down_test() -> int:
    return run([
        "docker", "compose", "-p", "tests", "-f", "docker-compose.test.yml",
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