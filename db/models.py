from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core import config


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Catalog(Base):
    __tablename__ = "catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    color_name: Mapped[str] = mapped_column(ForeignKey("tile_colors.name"))
    image_path: Mapped[str] = mapped_column(default=config.image_path)
    size_height: Mapped[float]
    size_width: Mapped[float]
    surface_name: Mapped[str] = mapped_column(ForeignKey("tile_surface.name"))
    material_name: Mapped[str] = mapped_column(ForeignKey("tile_materials.name"))
    producer_name: Mapped[str] = mapped_column(ForeignKey("producers.name"))
    box_weight_id: Mapped[int] = mapped_column(ForeignKey("box_weights.box_weight_id"))
    pallet_weight_id: Mapped[int] = mapped_column(
        ForeignKey("pallet_weights.pallet_weight_id")
    )

    color: Mapped["TileColor"] = relationship("TileColor", back_populates="tiles")
    size: Mapped["TileSize"] = relationship("TileSize", back_populates="tiles")
    surface: Mapped["TileSurface"] = relationship("TileSurface", back_populates="tiles")
    material: Mapped["TileMaterial"] = relationship(
        "TileMaterial", back_populates="tiles"
    )
    producer: Mapped["Producer"] = relationship("Producer", back_populates="tiles")
    box: Mapped["BoxWeight"] = relationship("BoxWeight", back_populates="tiles")
    pallet: Mapped["PalletWeight"] = relationship(
        "PalletWeight", back_populates="tiles"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["size_height", "size_width"],
            ["tile_sizes.height", "tile_sizes.width"],
        ),
    )

    def model_dump(self):
        data = {
            "id": self.id,
            "name": self.name,
            "size_height": self.size_height,
            "size_width": self.size_width,
            "color_name": self.color_name,
            "surface_name": self.surface_name,
            "material_name": self.material_name,
            "producer_name": self.producer_name,
            "image_path": self.image_path,
        }

        try:
            feature_name = getattr(self.color, "feature_name", None)
            box_weight = getattr(self.box, "weight", None)
            pallet_weight = getattr(self.pallet, "weight", None)
            if feature_name is not None:
                data["feature_name"] = feature_name
            if box_weight is not None:
                data["box_weight"] = box_weight
            if pallet_weight is not None:
                data["pallet_weight"] = pallet_weight
        except Exception:
            pass

        return data


class TileSize(Base):
    __tablename__ = "tile_sizes"
    height: Mapped[float] = mapped_column(primary_key=True)
    width: Mapped[float] = mapped_column(primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="size",
    )

    def model_dump(self):
        return {"height": self.height, "width": self.width}


class TileColorFeature(Base):
    __tablename__ = "tile_color_features"
    name: Mapped[str] = mapped_column(primary_key=True)
    colors: Mapped[list["TileColor"]] = relationship(
        "TileColor",
        back_populates="feature",
    )

    def model_dump(self):
        return {"name": self.name}


class TileColor(Base):
    __tablename__ = "tile_colors"
    name: Mapped[str] = mapped_column(primary_key=True)
    feature_name: Mapped[str] = mapped_column(ForeignKey("tile_color_features.name"))
    feature: Mapped["TileColorFeature"] = relationship(
        "TileColorFeature", back_populates="colors"
    )
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="color",
    )

    def model_dump(self):
        return {"name": self.name, "feature_name": self.feature_name}


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


class BoxWeight(Base):
    __tablename__ = "box_weights"
    box_weight_id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[float] = mapped_column(unique=True)
    tiles: Mapped[list["Catalog"]] = relationship("Catalog", back_populates="box")

    def model_dump(self):
        return {"weight": self.weight, "box_weight_id": self.box_weight_id}


class PalletWeight(Base):
    __tablename__ = "pallet_weights"
    pallet_weight_id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[float] = mapped_column(unique=True)
    tiles: Mapped[list["Catalog"]] = relationship("Catalog", back_populates="pallet")

    def model_dump(self):
        return {"weight": self.weight, "pallet_weight_id": self.pallet_weight_id}
