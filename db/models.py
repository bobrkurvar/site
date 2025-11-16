from sqlalchemy import ForeignKeyConstraint, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from core import config


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Catalog(Base):
    __tablename__ = "catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    color: Mapped[str]
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
            "image_path": self.image_path,
            "color": self.color
        }

class TileSize(Base):
    __tablename__ = 'tile_sizes'
    height: Mapped[float] = mapped_column(primary_key=True)
    width: Mapped[float] = mapped_column(primary_key=True)
    tiles: Mapped[list['Catalog']] = relationship("Catalog", back_populates='size')

    def model_dump(self):
        return {
            "height": self.height,
            "width": self.width
        }


class TileColorFeature(Base):
    __tablename__ = 'tile_color_features'
    name: Mapped[str] = mapped_column(primary_key=True)
    color: Mapped['TileColor'] = relationship('TileColor', back_populates='feat_name')


class TileColor(Base):
    __tablename__= 'tile_colors'
    name: Mapped[str] = mapped_column(primary_key=True)
    feature: Mapped[str] = mapped_column(ForeignKey('tile_color_features.name'))
    feat_name: Mapped['TileColorFeature'] = relationship("TileColorFeature", back_populates='color')