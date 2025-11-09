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

    def __init__(self, entity: str, field: str | None = None, value=None):
        self.field = field
        self.value = value
        self.entity = entity
        if field and value:
            super().__init__(
                f"Запись с {field} = {value} в таблице {entity} уже существует"
            )
        else:
            super().__init__(f"Запись с таким id в таблице {entity} уже существует")


class CustomForeignKeyViolationError(RepositoryError):
    """Ошибка внешнего ключа"""

    def __init__(self, entity: str, field: str, value):
        self.entity_name = entity
        self.field = field
        self.value = value
        super().__init__(
            f"Foreign key violation: {entity}.{field} = {value} references non-existent entity"
        )


class DatabaseError(RepositoryError):
    pass
