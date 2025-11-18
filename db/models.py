from sqlalchemy import ForeignKey, ForeignKeyConstraint, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core import config


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Catalog(Base):
    __tablename__ = "catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    color_name: Mapped[str] = mapped_column(
        ForeignKey("tile_colors.name", ondelete="CASCADE")
    )
    image_path: Mapped[str] = mapped_column(default=config.image_path)
    size_height: Mapped[float]
    size_width: Mapped[float]
    surface_name: Mapped[str] = mapped_column(
        ForeignKey("tile_surface.name", ondelete="CASCADE")
    )

    color: Mapped["TileColor"] = relationship("TileColor", back_populates="tiles")
    size: Mapped["TileSize"] = relationship("TileSize", back_populates="tiles")
    surface: Mapped["TileSurface"] = relationship("TileSurface", back_populates="tiles")

    __table_args__ = (
        ForeignKeyConstraint(
            ["size_height", "size_width"],
            ["tile_sizes.height", "tile_sizes.width"],
            ondelete="CASCADE",
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
            "image_path": self.image_path,
        }

        try:
            feature_name = getattr(self.color, 'feature_name', None)
            if feature_name is not None:
                data["feature_name"] = feature_name
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
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def model_dump(self):
        return {"height": self.height, "width": self.width}


class TileColorFeature(Base):
    __tablename__ = "tile_color_features"
    name: Mapped[str] = mapped_column(primary_key=True)
    colors: Mapped[list["TileColor"]] = relationship(
        "TileColor",
        back_populates="feature",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def model_dump(self):
        return {'name': self.name}


class TileColor(Base):
    __tablename__ = "tile_colors"
    name: Mapped[str] = mapped_column(primary_key=True)
    feature_name: Mapped[str] = mapped_column(
        ForeignKey("tile_color_features.name", ondelete="CASCADE")
    )
    feature: Mapped["TileColorFeature"] = relationship(
        "TileColorFeature", back_populates="colors"
    )
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="color",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def model_dump(self):
        return {
            "name": self.name,
            "feature_name": self.feature_name
        }

class TileSurface(Base):
    __tablename__ = "tile_surface"
    name: Mapped[str] = mapped_column(primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="surface",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def model_dump(self):
        return {"name": self.name}