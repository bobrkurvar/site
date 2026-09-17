import subprocess

from contextlib import contextmanager
from .commands import Down


class Compose:
    def __init__(self, *compose_files, project: str | None = None, allow_build = True):
        self.compose_files = compose_files
        self.project = project
        self.allow_build = allow_build

    def make_command(self, command) -> list[str]:
        command = list(command)

        if not self.allow_build:
            command = [
                arg
                for arg in command
                if arg != "--build"
            ]

        args = ["docker", "compose"]

        if self.project:
            args.extend(("-p", self.project))

        for compose_file in self.compose_files:
            args.extend(("-f", compose_file))

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
    def down_before_and_after(self, volumes=True):
        self.execute(Down(volumes=volumes))
        try:
            yield self
        finally:
            self.execute(Down(volumes=volumes))