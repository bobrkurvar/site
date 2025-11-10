from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from core import config


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Catalog(Base):
    __tablename__ = "catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    image_path: Mapped[str] = mapped_column(default=config.image_path)

    def model_dump(self):
        return {
            "id": self.id,
            "name": self.name
        }