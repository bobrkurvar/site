from .user import Admin

# ОШИБКИ БАЗЫ ДАННЫХ И РЕПОЗИТОРИЯ


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



# БАЗОВЫЕ ОШИБКИ АВТОРИЗАЦИИ


class UnauthorizedError(Exception):
    """Базовое исключение для всех проблем с доступом (HTTP 401)"""
    def __init__(self, detail: str):
        self.detail = detail
        # ИМЕННО ЗДЕСЬ строка навсегда улетает в ядро Питона (в self.args)
        super().__init__(self.detail)


class CredentialsValidateError(UnauthorizedError):
    def __init__(self):
        super().__init__("Не правильные учётные данные")


class UserLoginNotFoundError(NotFoundError):
    """Наследуется от NotFoundError, так как это ошибка поиска в БД при логине"""
    def __init__(self, username: str):
        super().__init__(Admin, username=username)


# БАЗОВЫЕ ОШИБКИ ТОКЕНОВ

class InvalidTokenError(UnauthorizedError):
    def __init__(self, token_type: str, reason: str = None):
        base_detail = f"Неправильный {token_type} token"
        # Конструируем строку формата "База: Уточнение"
        detail = f"{base_detail}: {reason}" if reason else base_detail
        super().__init__(detail)


# ACCESS ТОКЕНА

class InvalidAccessTokenError(InvalidTokenError):
    def __init__(self, reason: str = None):
        super().__init__(token_type="access", reason=reason)

class AccessTokenExpireError(InvalidAccessTokenError):
    def __init__(self):
        super().__init__(reason="Время жизни токена истекло")


class AccessTokenDecodedError(InvalidAccessTokenError):
    def __init__(self):
        super().__init__(reason="Ошибка декодирования токена")




# ОШИБКИ REFRESH ТОКЕНА

class InvalidRefreshTokenError(InvalidTokenError):
    def __init__(self, reason: str = None):
        super().__init__(token_type="refresh", reason=reason)

class RefreshTokenExpireError(InvalidRefreshTokenError):
    def __init__(self):
        super().__init__(reason="Время жизни токена истекло")

class RefreshTokenDecodedError(InvalidRefreshTokenError):
    def __init__(self):
        super().__init__(reason="Ошибка декодирования токена")

class RefreshTokenMissingError(InvalidRefreshTokenError):
    """Токен вообще не был передан в запросе (например, нет куки)"""
    def __init__(self):
        super().__init__(reason="токен не предоставлен в запросе")


# СПЕЦИФИЧНЫЕ ОШИБКИ REFRESH

class RefreshTokenMalformedError(InvalidRefreshTokenError):
    """Отсутствуют обязательные поля (jti, family_id) или неверная структура"""
    def __init__(self):
        super().__init__(reason="повреждена структура или отсутствуют обязательные поля")


class RefreshTokenReusedCompromisedError(InvalidRefreshTokenError):
    """БРЕШЬ: Попытка использовать токен повторно (возможна кража!)"""
    def __init__(self):
        super().__init__(reason="обнаружено повторное использование (возможна компрометация сессии)")


class RefreshTokenRotationRaceConditionError(InvalidRefreshTokenError):
    """Семья токенов удалена другим параллельным запросом (состояние гонки)"""
    def __init__(self):
        super().__init__(reason="конфликт обновления (состояние гонки)")


class RefreshTokenFamilyExpiredError(InvalidRefreshTokenError):
    """Токен формально жив, но его семья (rtfam) уже удалена из Redis"""
    def __init__(self):
        super().__init__(reason="сессия обновления не найдена или была принудительно завершена")


# СПЕЦИФИЧНЫЕ ОШИБКИ ACCESS
class AccessTokenMalformedError(InvalidAccessTokenError):
    """Отсутствуют обязательные поля (jti, family_id) или неверная структура"""
    def __init__(self):
        super().__init__(reason="повреждена структура или отсутствуют обязательные поля")