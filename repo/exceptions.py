class RepositoryError(Exception):
    """Базовое исключение репозитория"""

    pass


class NotFoundError(RepositoryError):
    """Не найдена запись в базе"""

    def __init__(self, entity_name: str, ident: str | None = None, ident_val=None):
        self.entity_name = entity_name
        self.ident = ident
        self.ident_val = ident_val
        if ident and ident_val:
            super().__init__(f"{entity_name} with {ident} = {ident_val} not found")
        else:
            super().__init__(f"{entity_name} not found")


class AlreadyExistsError(RepositoryError):
    """Запись с таким атрибутом уже существует в базе"""

    def __init__(self, model_name: str, constraint: str):
        self.model_name = model_name
        self.constraint = constraint
        super().__init__(f"{model_name} already exists (constraint: {constraint})")


class CustomForeignKeyViolationError(RepositoryError):
    """Ошибка внешнего ключа"""

    def __init__(self, model_name: str, detail: str):
        self.model_name = model_name
        self.detail = detail
        super().__init__(f"Foreign key violation in {model_name}: {detail}")

class DatabaseError(RepositoryError):
    pass
