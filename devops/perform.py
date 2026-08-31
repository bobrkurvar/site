import subprocess


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

    def run(self, *commands, check: bool = False) -> int:
        code = 0

        for command in commands:
            args = self.make_command(command)

            print(">", " ".join(args))

            result = subprocess.run(args)
            code = result.returncode

            if check:
                result.check_returncode()

        return code
