from .perform import Compose
from .commands import Run
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
