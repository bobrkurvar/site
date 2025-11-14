from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from core import config


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Catalog(Base):
    __tablename__ = "catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    image_path: Mapped[str] = mapped_column(default=config.image_path)
    size_height: Mapped[float]
    size_width: Mapped[float]

    size: Mapped['SizeTile'] = relationship("SizeTile", back_populates="tiles")

    __table_args__ = (
        ForeignKeyConstraint(
            ['size_height', 'size_width'],
            ['tile_size.height', 'tile_size.width']
        ),
    )

    def model_dump(self):
        return {
            "id": self.id,
            "name": self.name,
            "size_height": self.size_height,
            "size_width": self.size_width,
            "image_path": self.image_path
        }

class SizeTile(Base):
    __tablename__ = 'tile_size'
    height: Mapped[float] = mapped_column(primary_key=True)
    width: Mapped[float] = mapped_column(primary_key=True)
    tiles: Mapped[list['Catalog']] = relationship("Catalog", back_populates='size')

    def model_dump(self):
        return {
            "height": self.height,
            "width": self.width
        }