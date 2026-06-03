from sqlalchemy import text

from services.read_models import (CatalogFiltersDTO, FilterColorDTO,
                                  FilterSizeDTO)


class CatalogQueryService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_catalog_filters(
        self, category_slug: str | None = None, collection_slug: str | None = None
    ) -> CatalogFiltersDTO:
        sql = """
            WITH filtered_tiles AS (
                SELECT * FROM catalog
                WHERE 
                  (CAST(:cat_slug AS VARCHAR) IS NULL OR category_name = (SELECT name FROM slugs WHERE slug = :cat_slug))
                  AND (CAST(:col_slug AS VARCHAR) IS NULL OR name ILIKE '%' || (SELECT name FROM slugs WHERE slug = :col_slug) || '%')
            )
            SELECT 
                (SELECT json_agg(DISTINCT jsonb_build_object('id', ts.id, 'length', ts.length, 'width', ts.width, 'height', ts.height)) 
                 FROM filtered_tiles ft JOIN tile_sizes ts ON ft.size_id = ts.id) as sizes,

                (SELECT json_agg(DISTINCT jsonb_build_object('name', color_name, 'feature', feature_name)) 
                 FROM filtered_tiles) as colors,

                (SELECT array_agg(DISTINCT producer_name) 
                 FROM filtered_tiles) as producers;
        """

        async with self.session_factory.begin() as session:
            result = await session.execute(
                text(sql), {"cat_slug": category_slug, "col_slug": collection_slug}
            )
            raw_sizes, raw_colors, raw_producers = result.tuples().one()

            return CatalogFiltersDTO(
                sizes=[FilterSizeDTO(**s) for s in (raw_sizes or [])],
                colors=[FilterColorDTO(**c) for c in (raw_colors or [])],
                producers=list(raw_producers or []),
            )
