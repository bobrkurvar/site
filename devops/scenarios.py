from .perform import Compose
from .commands import Run, Down, Up, Logs
from .utils import failed_services

import json

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

# log_service = (
#     "app",
#     "postgres",
#     "nginx",
#     "image_service",
# )


def integration_tests():
    test_env.execute(Down(volumes=True))
    try:
        return test_env.execute(Run("int_tests", build=True), check=True)
    except:
        failed = failed_services(test_env)
        if failed:
            test_env.execute(Logs(*failed))
        raise
    finally:
        test_env.execute(Down(volumes=True))


