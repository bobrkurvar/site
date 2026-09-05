import json
from .commands import Ps, Logs
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

def execute_with_diagnostics(
    compose: Compose,
    *commands,
    **execute_kwargs,
):
    execute_kwargs["check"] = True

    try:
        return compose.execute(
            *commands,
            **execute_kwargs,
        )
    except Exception:
        failed = failed_services(compose)
        if failed:
            compose.execute(Logs(*failed))
        raise