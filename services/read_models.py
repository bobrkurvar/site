from dataclasses import dataclass

@dataclass(frozen=True)
class FilterSizeDTO:
    id: int
    length: int
    width: int
    height: int

    @property
    def present(self) -> str:
        """Для отображения человеку в интерфейсе"""
        return f"{self.length} × {self.width} × {self.height}"

    @property
    def value(self) -> str:
        """Для скрытого поля value в HTML / URL"""
        return f"{self.length} {self.width} {self.height}"


@dataclass(frozen=True)
class FilterColorDTO:
    name: str
    feature: str | None = None


@dataclass
class CatalogFiltersDTO:
    sizes: list[FilterSizeDTO]
    colors: list[FilterColorDTO]
    producers: list[str]