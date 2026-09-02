import json
from .commands import Ps
from .perform import Compose

def failed_services(compose_env: Compose) -> tuple[str, ...]:
    result = compose_env.execute(Ps(all=True, format="json"), capture_output=True)

    containers = (
        json.loads(line)
        for line in result.stdout.splitlines()
        if line
    )

    return tuple(
        container["Service"]
        for container in containers
        if container["ExitCode"] != 0
    )