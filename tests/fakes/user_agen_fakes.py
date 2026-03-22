class FakeCookieManager:

    def __init__(self, request = None, response = None):
        self.request = request
        self.response = response
        self.storage = {}
        self.refresh_token_key = "refresh_token"
        self.access_token_key = "access_token"

    def get_refresh_token(self):
        return self.storage.get(self.refresh_token_key)

    def get_access_token(self):
        return self.storage.get(self.access_token_key)

    def set_refresh_token(self, value):
        self.storage[self.refresh_token_key] = value

    def set_access_token(self, value):
        self.storage[self.access_token_key] = value
