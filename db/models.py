from decimal import Decimal
from pathlib import Path

from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL

from core import config


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Catalog(Base):
    __tablename__ = "catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    color_name: Mapped[str]
    feature_name: Mapped[str]
    size_id: Mapped[int] = mapped_column(ForeignKey("tile_sizes.id"))
    box_id: Mapped[int] = mapped_column(ForeignKey("boxes.id"))
    surface_name: Mapped[str] = mapped_column(
        ForeignKey("tile_surface.name"), nullable=True
    )
    producer_name: Mapped[str] = mapped_column(ForeignKey("producers.name"))
    category_name: Mapped[str] = mapped_column(ForeignKey("categories.name"))
    boxes_count: Mapped[int]

    color: Mapped["TileColor"] = relationship("TileColor", back_populates="tiles")
    size: Mapped["TileSize"] = relationship("TileSize", back_populates="tiles")
    surface: Mapped["TileSurface"] = relationship("TileSurface", back_populates="tiles")
    producer: Mapped["Producer"] = relationship("Producer", back_populates="tiles")
    box: Mapped["Box"] = relationship("Box", back_populates="tiles")
    images: Mapped[list["TileImages"]] = relationship(
        "TileImages",
        back_populates="tile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    category: Mapped["Categories"] = relationship("Categories", back_populates="tiles")

    __table_args__ = (
        ForeignKeyConstraint(
            ["color_name", "feature_name"],
            ["tile_colors.color_name", "tile_colors.feature_name"],
        ),
    )

    def model_dump(self):
        data = {
            "id": self.id,
            "name": self.name,
            "box_id": self.box_id,
            "color_name": self.color_name,
            "feature_name": self.feature_name,
            "surface_name": self.surface_name,
            "producer_name": self.producer_name,
            "boxes_count": self.boxes_count,
            "category_name": self.category_name,
            "size_id": self.size_id,
        }

        try:
            if self.images:
                data["images_paths"] = [
                    '\\'+str(p.image_path)
                    for p in self.images
                ]
        except Exception:
            pass

        try:
            if self.size:
                data["size_length"] = self.size.length
                data["size_height"] = self.size.height
                data["size_width"] = self.size.width
        except Exception:
            pass

        try:
            if self.box:
                data["box_weight"] = self.box.weight
                data["box_area"] = self.box.area
        except Exception:
            pass

        return data


class Categories(Base):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship("Catalog", back_populates="category")

    collections: Mapped[list["Collections"]] = relationship("Collections", back_populates="category")

    def model_dump(self):
        return {"name": self.name}


class TileImages(Base):
    __tablename__ = "tile_images"
    image_id: Mapped[int] = mapped_column(primary_key=True)
    tile_id: Mapped[int] = mapped_column(ForeignKey("catalog.id", ondelete="CASCADE"))
    image_path: Mapped[str] = mapped_column(default=config.image_path)
    tile: Mapped["Catalog"] = relationship("Catalog", back_populates="images")

    def model_dump(self):
        return {
            "image_id": self.image_id,
            "tile_id": self.tile_id,
            "image_path": self.image_path,
        }


class Collections(Base):
    __tablename__ = "collections"
    name: Mapped[str] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(ForeignKey("categories.name"), primary_key=True)
    image_path: Mapped[str] = mapped_column(unique=True, default=config.image_path)

    category: Mapped["Categories"] = relationship("Categories", back_populates="collections")

    def model_dump(self):
        return {"name": self.name, "image_path": self.image_path, "category_name": self.category_name}


class TileSize(Base):
    __tablename__ = "tile_sizes"
    id: Mapped[int] = mapped_column(primary_key=True)
    length: Mapped[Decimal] = mapped_column(DECIMAL(7, 2))
    height: Mapped[Decimal] = mapped_column(DECIMAL(7, 2))
    width: Mapped[Decimal] = mapped_column(DECIMAL(7, 2))
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="size",
    )

    __table_args__ = (UniqueConstraint("length", "width", "height"),)

    def model_dump(self):
        return {
            "id": self.id,
            "length": self.length,
            "height": self.height,
            "width": self.width,
        }


class TileColor(Base):
    __tablename__ = "tile_colors"
    color_name: Mapped[str] = mapped_column(primary_key=True)
    feature_name: Mapped[str] = mapped_column(primary_key=True, default="")
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="color",
    )

    def model_dump(self):
        return {"color_name": self.color_name, "feature_name": self.feature_name}


class TileSurface(Base):
    __tablename__ = "tile_surface"
    name: Mapped[str] = mapped_column(primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="surface",
    )

    def model_dump(self):
        return {"name": self.name}


class Producer(Base):
    __tablename__ = "producers"
    name: Mapped[str] = mapped_column(primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="producer",
    )

    def model_dump(self):
        return {"name": self.name}


class Box(Base):
    __tablename__ = "boxes"
    id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    area: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    tiles: Mapped[list["Catalog"]] = relationship("Catalog", back_populates="box")

    __table_args__ = (UniqueConstraint("weight", "area"),)

    def model_dump(self):
        return {"id": self.id, "weight": self.weight, "area": self.area}
