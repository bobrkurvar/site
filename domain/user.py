class Admin:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password


class Slug:
    def __init__(self, name: str):
        self.name = name