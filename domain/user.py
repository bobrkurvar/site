from slugify import slugify


class Admin:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class Slug:
    def __init__(self, name: str, slug: str | None = None):
        self.name = name
        self.slug = slug if slug is not None else slugify(self.name)
