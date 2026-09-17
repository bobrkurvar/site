from .perform import Compose
from .commands import Run, Up
from .utils import execute_with_diagnostics
import shlex


base = "docker-compose.base.yml"

prod_env = Compose(
    base,
    "docker-compose.prod.yml",
    project="site",
    allow_build=False
)

test_env = Compose(
    base,
    "docker-compose.test.yml",
    project="tests",
)

local_env = Compose(
    base,
    "docker-compose.local.yml",
    project="local_site",
)


def integration_tests(*args):
    with test_env.down_before_and_after() as compose:
        return execute_with_diagnostics(
            compose,
            Run("int_tests", build=True, command=args),
            #diagnostic_services=("image_service", )
        )


def unit_tests(*args):
    with test_env.down_before_and_after() as compose:
        return execute_with_diagnostics(compose, Run("unit_tests", build=True, command=args))


def e2e_tests(*args):
    with test_env.down_before_and_after() as compose:
        return execute_with_diagnostics(
            compose,
            Run("e2e_tests", build=True, command=args),
            diagnostic_services=("app", "nginx"),
        )


def all_tests():
    with test_env.down_before_and_after() as compose:
        execute_with_diagnostics(
            compose,
            Run("unit_tests", build=True),
            Run("int_tests", build=True),
            Run("e2e_tests", build=True),
        )


def deploy(compose: Compose, build=True):
    with compose.down_before_and_after(volumes=False):
        execute_with_diagnostics(compose, Up(build=build))


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


def migrate(compose: Compose, build=True):
     return execute_with_diagnostics(compose,Run("migrate", build=build))



def generate_miniatures(compose: Compose, build=True):
    return execute_with_diagnostics(compose, Run("generate_miniatures", build=build))


def rename_collections(compose: Compose, build=True):
    with compose.down_before_and_after(volumes=False):
        return execute_with_diagnostics(compose, Run("rename_collections", build=build))


def interactive(env: Compose, *args):
    if args:
        return env.execute(args)

    while True:
        try:
            command = input("compose> ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            return

        if not command:
            continue

        if command in {"exit", "quit"}:
            return

        env.execute(shlex.split(command))