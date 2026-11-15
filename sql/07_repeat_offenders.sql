-- Are misfits spread thinly, or do a few items collect most of them?
-- Each item is put in a band by how many misfit reviews it has. Then we
-- count how many items, and what share of all misfit reviews, fall in each band.
WITH item_misfits AS (
    SELECT
        item_id,
        COUNT(*) FILTER (WHERE fit <> 'fit') AS misfit_reviews
    FROM reviews
    GROUP BY item_id
),
banded AS (
    SELECT
        item_id,
        misfit_reviews,
        CASE
            WHEN misfit_reviews = 0  THEN '0'
            WHEN misfit_reviews < 5  THEN '1-4'
            WHEN misfit_reviews < 20 THEN '5-19'
            WHEN misfit_reviews < 50 THEN '20-49'
            ELSE '50+'
        END AS misfit_band
    FROM item_misfits
)
SELECT
    misfit_band,
    COUNT(*)                                         AS items,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM banded), 1)                          AS items_pct,
    CAST(SUM(misfit_reviews) AS INTEGER)             AS misfit_reviews,
    ROUND(100.0 * SUM(misfit_reviews) / (SELECT SUM(misfit_reviews) FROM banded), 1)    AS misfit_share_pct
FROM banded
GROUP BY misfit_band
ORDER BY MIN(misfit_reviews);
