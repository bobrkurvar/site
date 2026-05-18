from dataclasses import dataclass
from typing import Any

@dataclass
class DomainFilter:
    model: type      # Доменная модель (например, Category)
    field: str       # Имя поля (например, 'name')
    value: Any       # Значение (например, 'Керамика')


@dataclass
class Operation:
    value: Any
    op: str = "exact"  # По умолчанию обычное равенство