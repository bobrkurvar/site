from decimal import Decimal

from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL

from core import conf


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
    images: Mapped[list["TileImage"]] = relationship(
        "TileImage",
        back_populates="tile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    category: Mapped["Category"] = relationship("Category", back_populates="tiles")
    collections: Mapped[list["Collection"]] = relationship(
        "Collection",
        secondary="collection_category",
        primaryjoin="Catalog.category_name == CollectionCategory.category_name",
        secondaryjoin="CollectionCategory.collection_id == Collection.id",
        viewonly=True,  # Только для чтения
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["color_name", "feature_name"],
            ["tile_colors.color_name", "tile_colors.feature_name"],
        ),
    )


class Category(Base):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship("Catalog", back_populates="category")

    collections: Mapped[list["CollectionCategory"]] = relationship(
        "CollectionCategory",
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TileImage(Base):
    __tablename__ = "tile_images"
    image_id: Mapped[int] = mapped_column(primary_key=True)
    tile_id: Mapped[int] = mapped_column(ForeignKey("catalog.id", ondelete="CASCADE"))
    image_path: Mapped[str] = mapped_column(default=conf.image_path)
    tile: Mapped["Catalog"] = relationship("Catalog", back_populates="images")


class Collection(Base):
    __tablename__ = "collections"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    image_path: Mapped[str] = mapped_column(unique=True, nullable=True)
    categories: Mapped[list["CollectionCategory"]] = relationship(
        "CollectionCategory",
        back_populates="collection",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    # noinspection PyTypeChecker
    categories_proxy: AssociationProxy[list[str]] = association_proxy(
        "categories",
        "category_name",
        creator=lambda cat_name: CollectionCategory(category_name=cat_name),
    )


class CollectionCategory(Base):
    __tablename__ = "collection_category"
    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    category_name: Mapped[str] = mapped_column(
        ForeignKey("categories.name", ondelete="CASCADE"), primary_key=True
    )

    category: Mapped["Category"] = relationship(
        "Category", back_populates="collections"
    )
    collection: Mapped["Collection"] = relationship(
        "Collection", back_populates="categories"
    )


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


class TileColor(Base):
    __tablename__ = "tile_colors"
    color_name: Mapped[str] = mapped_column(primary_key=True)
    feature_name: Mapped[str] = mapped_column(primary_key=True, default="")
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="color",
    )


class TileSurface(Base):
    __tablename__ = "tile_surface"
    name: Mapped[str] = mapped_column(primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="surface",
    )


class Producer(Base):
    __tablename__ = "producers"
    name: Mapped[str] = mapped_column(primary_key=True)
    tiles: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="producer",
    )


class Box(Base):
    __tablename__ = "boxes"
    id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    area: Mapped[Decimal] = mapped_column(DECIMAL(8, 2))
    tiles: Mapped[list["Catalog"]] = relationship("Catalog", back_populates="box")

    __table_args__ = (UniqueConstraint("weight", "area"),)


class Admin(Base):
    __tablename__ = "admins"
    username: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str]
