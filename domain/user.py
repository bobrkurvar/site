from slugify import slugify

class Admin:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class Slug:
    def __init__(self, name: str):
        self.name = name
        self.slug = slugify(name)
