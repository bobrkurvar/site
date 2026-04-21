import subprocess
import sys


PROD_PROJECT = "site"
PROD_COMPOSE = "docker-compose.yml"
TEST_PROJECT = "tests"
TEST_COMPOSE = "docker-compose.test.yml"
IS_TEST = False


def run(cmd: list[str]) -> int:
    print(">", " ".join(cmd))
    return subprocess.call(cmd)

def run_or_exit(cmd):
    code = run(cmd)
    if code != 0:
        sys.exit(code)

def compose_run(*args):
    return ["docker", "compose", "-p", TEST_PROJECT if IS_TEST else PROD_PROJECT, "-f", TEST_COMPOSE if IS_TEST else PROD_COMPOSE, *args]


def test():
    global IS_TEST
    IS_TEST = True

    e2e_code = 0
    int_code = 0
    try:
        run_or_exit(compose_run("up", "--build", "-d", "postgres", "migrate", "runner", "app"))
        run_or_exit(compose_run("build", "e2e_tests"))
        e2e_code = run(compose_run("run", "--rm", "--no-deps", "e2e_tests"))
        run_or_exit(compose_run("build", "int_tests"))
        int_code = run(compose_run("run", "--rm", "--no-deps", "int_tests"))
    finally:
        run(compose_run("down", "-v", "--remove-orphans"))
        return e2e_code or int_code


def scripts_run():
    admins = input("Script add_admins(y/n): ")
    if admins.strip().lower() == "y":
        run_or_exit(compose_run("build", "runner"))
        run_or_exit(compose_run("run", "--rm", "runner"))
    resize_images = input("Script resize_images(y/n): ")
    if resize_images.strip().lower() == "y":
        run_or_exit(compose_run("build", "resize-images-script"))
        run_or_exit(compose_run("run", "--rm", "resize-images-script"))
    return 0


def prod() -> int:
    scripts = input("run the init scripts (y/n): ")
    if scripts.strip().lower() == "y":
        return scripts_run()
    return run(compose_run("up", "--build"))

def down() -> int:
    return run(compose_run("down", "--remove-orphans"))

def down_test() -> int:
    global IS_TEST
    IS_TEST = True
    return run(compose_run("down", "--remove-orphans"))

def logs():
    services = ["app", "image_service"]
    outs = "|".join(services)
    out = input(f"[{outs}]: ")
    if out in services:
        return run(compose_run("logs", "-f", out))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [test|prod|down|down-test|logs]")
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
    elif cmd == "logs":
        code = logs()
    else:
        print(f"Unknown command: {cmd}")
        code = 1

    sys.exit(code)