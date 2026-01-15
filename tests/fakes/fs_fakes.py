class FakeAsyncFile:
    def __init__(self, path, mode, filesystem):
        self.path = path
        self.mode = mode
        self.fs = filesystem
        self.written_data = b""

    async def write(self, data):
        self.written_data += data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.fs.files[self.path] = self.written_data


class FakeFileSystem:
    def __init__(self):
        self.files = {}  # path -> bytes

    def open(self, path, mode):
        return FakeAsyncFile(path, mode, self)


class FakePath:
    def __init__(self, *parts, fs=None):
        self.parts = list(parts)
        self.fs = fs

    def __truediv__(self, other):
        return FakePath(*self.parts, str(other), fs=self.fs)

    def mkdir(self, parents=False, exist_ok=False):
        pass

    def exists(self):
        return str(self) in self.fs.files if self.fs is not None else None

    def unlink(self):
        del self.fs.files[str(self)]

    def __str__(self):
        return "/".join(self.parts)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)
