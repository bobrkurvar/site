from fastapi import status

class UnauthorizedError(Exception):
    """
    Исключение, которое будет возбуждено вследствие
    попытке доступа к защищённому ресурсу без аутентификации
    """

    def __init__(self, validate: bool = None, refresh_token: bool = None, access_token: bool | None = None):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.headers = {"WWW-Authenticate": "Bearer"}
        if validate:
            self.detail = (
                f"Попытка не аутентифицированного доступа, не валидные учётные данные"
            )
        elif refresh_token:
            self.detail = (
                f"Попытка не аутентифицированного доступа, refresh token истёк"
            )
        elif access_token:
            self.detail = (
                f"Попытка не аутентифицированного доступа, access token истёк"
            )
        else:
            self.detail = f"Попытка не аутентифицированного доступа"
        super().__init__(self.detail)
