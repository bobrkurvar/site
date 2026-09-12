from sqlalchemy import text

from services.read_models import CatalogFiltersDTO, FilterColorDTO, FilterSizeDTO


class CatalogQueryService:
    def __init__(self, session):
        #self.session_factory = session_factory
        self.session = session

    async def get_catalog_filters(
        self,
        category_id: int,
        collection_id: int | None = None,
    ) -> CatalogFiltersDTO:
        sql = """
            WITH selected_collection AS (
                SELECT c.name
                FROM collections c
                JOIN collection_category cc
                    ON cc.collection_id = c.id
                WHERE
                    c.id = :collection_id
                    AND cc.category_id = :category_id
            ),
            filtered_tiles AS (
                SELECT t.*
                FROM tiles t
                WHERE
                    t.category_id = :category_id
                    AND (
                        CAST(:collection_id AS INTEGER) IS NULL
                        OR t.name ILIKE (
                            '%' || '"' ||
                            (SELECT name FROM selected_collection) ||
                            '"' || '%'
                        )
                    )
            )
            SELECT
                (
                    SELECT json_agg(DISTINCT jsonb_build_object(
                        'id', ts.id,
                        'length', ts.length,
                        'width', ts.width,
                        'height', ts.height
                    ))
                    FROM filtered_tiles ft
                    JOIN tile_sizes ts ON ft.size_id = ts.id
                ) AS sizes,
            
                (
                    SELECT json_agg(DISTINCT jsonb_build_object(
                        'name', ft.color_name,
                        'feature', ft.feature_name
                    ))
                    FROM filtered_tiles ft
                ) AS colors,
            
                (
                    SELECT array_agg(DISTINCT ft.producer_name)
                    FROM filtered_tiles ft
                ) AS producers;
        """

        #async with self.session_factory.begin() as session:
        result = await self.session.execute(
            text(sql),
            {
                "category_id": category_id,
                "collection_id": collection_id,
            },
        )
        raw_sizes, raw_colors, raw_producers = result.tuples().one()

        return CatalogFiltersDTO(
            sizes=[FilterSizeDTO(**s) for s in (raw_sizes or [])],
            colors=[FilterColorDTO(**c) for c in (raw_colors or [])],
            producers=list(raw_producers or []),
        )
