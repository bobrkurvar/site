from .perform import Compose
from .commands import Run, Down, Up, Logs

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

log_service = (
    "app",
    "postgres",
    "nginx",
    "image_service",
)


def integration_tests():
    test_env.run(Down(volumes=True))
    try:
        return test_env.run(Run("int_tests", build=True))
    finally:
        test_env.run(Down(volumes=True))


def show_logs(compose: Compose, *, follow: bool = True):
    services = "|".join(log_service)
    service = input(f"[{services}]: ").strip()

    if service not in log_service:
        return

    compose.run(
        Logs(
            service,
            follow=follow,
        )
    )
