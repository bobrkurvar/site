def token_setter_with_storage(storage: dict):
    def token_setter(key: str, token, ttl=None):
        storage[key] = token
    return token_setter

def token_getter_with_storage(storage: dict):
    def token_getter(key: str):
        return storage.get(key, None)
    return token_getter