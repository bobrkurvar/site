import subprocess
import sys


PROD_PROJECT = "site"
PROD_COMPOSE = "docker-compose.yml"
TEST_PROJECT = "tests"
TEST_COMPOSE = "docker-compose.test.yml"
LOCAL_PROJECT = "local_site"
LOCAL_COMPOSE = "docker-compose.local.yml"


PROJECT = PROD_PROJECT
COMPOSE = PROD_COMPOSE

def set_project(is_prod=False, is_test = False, is_local=False):
    global PROJECT, COMPOSE
    if is_prod:
        PROJECT = PROD_PROJECT
        COMPOSE = PROD_COMPOSE
    elif is_test:
        PROJECT = TEST_PROJECT
        COMPOSE = TEST_COMPOSE
    elif is_local:
        PROJECT = LOCAL_PROJECT
        COMPOSE = LOCAL_COMPOSE


def run(cmd: list[str]) -> int:
    print(">", " ".join(cmd))
    return subprocess.call(cmd)


def run_or_exit(cmd):
    code = run(cmd)
    if code != 0:
        sys.exit(code)


def compose_run(*args):
    return [
        "docker",
        "compose",
        "-p",
        PROJECT,
        "-f",
        COMPOSE,
        *args,
    ]


def logs():
    services = ["app", "postgres", "nginx"]
    outs = "|".join(services)
    out = ""
    while out not in services:
        out = input(f"[{outs}]: ").strip()
    return run(compose_run("logs", out))


def test():
    global IS_TEST
    IS_TEST = True
    run(compose_run("down", "-v", "--remove-orphans"))
    e2e_code = 0
    int_code = 0
    try:
        tests = ""
        while tests not in {"int", "e2e", "all"}:
            tests = input("[int|e2e|all]: ").strip()
        run_or_exit(
            compose_run(
                "up",
                "--build",
                "-d",
                "postgres",
                "app",
                "nginx",
                "redis",
            )
        )
        run_or_exit(compose_run("run", "--rm", "--build", "migrate"))
        run_or_exit(compose_run("run", "--rm", "--build", "runner"))
        if tests in {"e2e", "all"}:
            run_or_exit(compose_run("build", "e2e_tests"))
            e2e_code = run(compose_run("run", "--rm", "e2e_tests"))
        if tests in {"int", "all"}:
            run_or_exit(compose_run("build", "int_tests"))
            int_code = run(compose_run("run", "--rm", "int_tests"))
        logs()
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


def prod() -> int:
    scripts = input("run the init scripts (y/n): ")
    if scripts.strip().lower() == "y":
        scripts_run()
    return run(compose_run("up", "--build", "--force-recreate"))


def down() -> int:
    docker = ("down", "--remove-orphans")
    if input("With volumes(y/n): ").strip() in {"y", "yes"}:
        cmd = compose_run(*docker, "-v")
    else:
        cmd = compose_run(*docker)
    return run(cmd)


def down_test() -> int:
    global IS_TEST
    IS_TEST = True
    return run(compose_run("down", "--remove-orphans"))


def local():
    scripts = input("run the init scripts (y/n): ")
    if scripts.strip().lower() == "y":
        scripts_run()
    return run(compose_run("up", "--build", "--force-recreate"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [test|prod|local|down|down-test|logs]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "test":
        set_project(is_test=True)
        code = test()
    elif cmd == "prod":
        set_project(is_prod=True)
        code = prod()
    elif cmd == "local":
        set_project(is_local=True)
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
