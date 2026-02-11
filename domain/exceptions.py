from enum import Enum


class RepositoryError(Exception):
    """Базовое исключение репозитория"""

    pass


class NotFoundError(RepositoryError):
    """Не найдена запись в базе"""

    def __init__(self, entity_name, **filters):
        self.entity_name = entity_name
        self.filters = filters
        if filters:
            super().__init__(f"{entity_name} with {filters}")
        else:
            super().__init__(f"{entity_name} not found")


class AlreadyExistsError(RepositoryError):
    """Запись с таким атрибутом уже существует в базе"""

    def __init__(self, model_name: str, constraint: str):
        self.model_name = model_name
        self.constraint = constraint
        super().__init__(f"{model_name} already exists (constraint: {constraint})")


class ForeignKeyViolationError(RepositoryError):
    """Ошибка внешнего ключа"""

    def __init__(self, model_name: str, detail: str):
        self.model_name = model_name
        self.detail = detail
        super().__init__(f"Foreign key violation in {model_name}: {detail}")


class AuthErrors(Enum):
    validate = "validate error"
    refresh = "refresh token error"
    access = "access token error"
    unexpected = "unexpected error"


class UnauthorizedError(Exception):
    """Ошибка внешнего ключа"""

    """
    Исключение, которое будет возбуждено вследствие
    попытке доступа к защищённому ресурсу без аутентификации
    """

    def __init__(
        self,
        validate: bool = None,
        refresh_token: bool = None,
        access_token: bool | None = None,
    ):
        self.headers = {"WWW-Authenticate": "Bearer"}
        if validate:
            self.error = AuthErrors.validate
            self.detail = (
                f"Попытка не аутентифицированного доступа, не валидные учётные данные"
            )
        elif refresh_token:
            self.error = AuthErrors.refresh
            self.detail = (
                f"Попытка не аутентифицированного доступа, refresh token истёк"
            )
        elif access_token:
            self.error = AuthErrors.access
            self.detail = f"Попытка не аутентифицированного доступа, access token истёк"
        else:
            self.error = AuthErrors.unexpected
            self.detail = f"Попытка не аутентифицированного доступа"
        super().__init__(self.detail)
