import subprocess

from contextlib import contextmanager
from .commands import Down


class Compose:
    def __init__(self, compose_file: str, *, project: str | None = None):
        self.compose_file = compose_file
        self.project = project

    def make_command(self, command) -> list[str]:
        args = ["docker", "compose"]

        if self.project:
            args.extend(("-p", self.project))

        args.extend(("-f", self.compose_file))
        args.extend(command)

        return args

    def execute(self, *commands, check: bool = False, capture_output=False):
        result = None

        for command in commands:
            args = self.make_command(command)

            print(">", " ".join(args))

            result = subprocess.run(
                args,
                capture_output=capture_output,
                text=capture_output,
            )

            if check:
                result.check_returncode()

        return result


    @contextmanager
    def down_before_and_after(self):
        self.execute(Down(volumes=True))
        try:
            yield self
        finally:
            self.execute(Down(volumes=True))