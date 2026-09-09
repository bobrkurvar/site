from .perform import Compose
from .commands import Run, Up
from .utils import execute_with_diagnostics


prod_env = Compose(
    "docker-compose.yml",
    project="site",
)

test_env = Compose(
    "docker-compose.test.yml",
    project="tests",
)

local_env = Compose(
    "docker-compose.local.yml",
    project="local_site",
)


def integration_tests(*args):
    with test_env.down_before_and_after() as compose:
        return execute_with_diagnostics(compose, Run("int_tests", build=True, command=args))


def unit_tests(*args):
    with test_env.down_before_and_after() as compose:
        return execute_with_diagnostics(compose, Run("unit_tests", build=True, command=args))


def e2e_tests(*args):
    with test_env.down_before_and_after() as compose:
        return execute_with_diagnostics(compose, Run("e2e_tests", build=True, command=args))


def all_tests():
    with test_env.down_before_and_after() as compose:
        execute_with_diagnostics(
            compose,
            Run("unit_tests", build=True),
            Run("int_tests", build=True),
            Run("e2e_tests", build=True),
        )


def local_deploy():
    with local_env.down_before_and_after() as compose:
        execute_with_diagnostics(compose, Up(build=True))


def create_migration(name: str | None = None):
    if name is None:
        name = input("Введите имя для миграции: ")

    return execute_with_diagnostics(
        local_env,
        Run(
            "migrate",
            build=True,
            command=("revision", "--autogenerate", "-m", name),
        )
    )


def migrate():
    return execute_with_diagnostics(local_env,Run("migrate"))