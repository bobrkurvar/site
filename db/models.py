from decimal import Decimal

from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL

from core import config


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Catalog(Base):
    __tablename__ = "catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    color_name: Mapped[str]
    feature_name: Mapped[str]
    image_path: Mapped[str] = mapped_column(default=config.image_path)
    size_height: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    size_width: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    box_weight: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    box_area: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    pallet_weight: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    pallet_area: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    surface_name: Mapped[str] = mapped_column(ForeignKey("tile_surface.name"))
    material_name: Mapped[str] = mapped_column(ForeignKey("tile_materials.name"))
    producer_name: Mapped[str] = mapped_column(ForeignKey("producers.name"))

    color: Mapped["TileColor"] = relationship("TileColor", back_populates="tiles")
    size: Mapped["TileSize"] = relationship("TileSize", back_populates="tiles")
    surface: Mapped["TileSurface"] = relationship("TileSurface", back_populates="tiles")
    material: Mapped["TileMaterial"] = relationship(
        "TileMaterial", back_populates="tiles"
    )
    producer: Mapped["Producer"] = relationship("Producer", back_populates="tiles")
    box: Mapped["Box"] = relationship("Box", back_populates="tiles")
    pallet: Mapped["Pallet"] = relationship("Pallet", back_populates="tiles")

    __table_args__ = (
        ForeignKeyConstraint(
            ["size_height", "size_width"],
            ["tile_sizes.height", "tile_sizes.width"],
        ),
        ForeignKeyConstraint(
            ["box_weight", "box_area"],
            ["boxes.weight", "boxes.area"],
        ),
        ForeignKeyConstraint(
            ["pallet_weight", "pallet_area"],
            ["pallets.weight", "pallets.area"],
        ),
        ForeignKeyConstraint(
            ["color_name", "feature_name"],
            ["tile_colors.color_name", "tile_colors.feature_name"],
        ),
    )

    def model_dump(self):
        data = {
            "id": self.id,
            "name": self.name,
            "size_height": self.size_height,
            "size_width": self.size_width,
            "color_name": self.color_name,
            "feature_name": self.feature_name,
            "surface_name": self.surface_name,
            "material_name": self.material_name,
            "producer_name": self.producer_name,
            "box_weight": self.box_weight,
            "box_area": self.box_area,
            "pallet_weight": self.pallet_weight,
            "pallet_area": self.pallet_area,
            "image_path": self.image_path,
        }

        return data


class TileSize(Base):
    __tablename__ = "tile_sizes"
    height: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), primary_key=True)
    width: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="size",
    )

    def model_dump(self):
        return {"height": self.height, "width": self.width}


class TileColor(Base):
    __tablename__ = "tile_colors"
    color_name: Mapped[str] = mapped_column(primary_key=True)
    feature_name: Mapped[str] = mapped_column(primary_key=True)
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


class TileMaterial(Base):
    __tablename__ = "tile_materials"
    name: Mapped[str] = mapped_column(primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="material",
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
    weight: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), primary_key=True)
    area: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship("Catalog", back_populates="box")

    def model_dump(self):
        return {"weight": self.weight, "area": self.area}


class Pallet(Base):
    __tablename__ = "pallets"
    weight: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), primary_key=True)
    area: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship("Catalog", back_populates="pallet")

    def model_dump(self):
        return {"weight": self.weight, "area": self.area}
