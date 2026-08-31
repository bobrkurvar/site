from dataclasses import dataclass


@dataclass(frozen=True)
class Run:
    service: str
    remove: bool = True
    build: bool = False
    dependencies: bool = True
    command: tuple[str, ...] = ()
    extra_args: tuple[str, ...] = ()

    @property
    def args(self) -> tuple[str, ...]:
        args = ["run"]

        if self.remove:
            args.append("--rm")

        if self.build:
            args.append("--build")

        if not self.dependencies:
            args.append("--no-deps")

        args.extend(self.extra_args)
        args.append(self.service)
        args.extend(self.command)

        return tuple(args)

    def __iter__(self):
        return iter(self.args)


class Up:
    def __init__(
        self,
        *services: str,
        build: bool = False,
        wait: bool = False,
        detach: bool = False,
        extra_args: tuple[str, ...] = (),
    ):
        self.services = services
        self.build = build
        self.wait = wait
        self.detach = detach
        self.extra_args = extra_args

    @property
    def args(self) -> tuple[str, ...]:
        args = ["up"]

        if self.build:
            args.append("--build")

        if self.wait:
            args.append("--wait")

        if self.detach:
            args.append("--detach")

        args.extend(self.extra_args)
        args.extend(self.services)

        return tuple(args)

    def __iter__(self):
        return iter(self.args)


@dataclass(frozen=True)
class Down:
    volumes: bool = False
    remove_orphans: bool = True
    extra_args: tuple[str, ...] = ()

    @property
    def args(self) -> tuple[str, ...]:
        args = ["down"]

        if self.volumes:
            args.append("--volumes")

        if self.remove_orphans:
            args.append("--remove-orphans")

        args.extend(self.extra_args)

        return tuple(args)

    def __iter__(self):
        return iter(self.args)


class Logs:
    def __init__(
        self,
        *services: str,
        follow: bool = False,
        tail: int | None = None,
        timestamps: bool = False,
        extra_args: tuple[str, ...] = (),
    ):
        self.services = services
        self.follow = follow
        self.tail = tail
        self.timestamps = timestamps
        self.extra_args = extra_args

    @property
    def args(self) -> tuple[str, ...]:
        args = ["logs"]

        if self.follow:
            args.append("--follow")

        if self.tail is not None:
            args.extend(("--tail", str(self.tail)))

        if self.timestamps:
            args.append("--timestamps")

        args.extend(self.extra_args)
        args.extend(self.services)

        return tuple(args)

    def __iter__(self):
        return iter(self.args)
