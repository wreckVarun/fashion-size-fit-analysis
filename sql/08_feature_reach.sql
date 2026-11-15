-- If we tag the flagged items from query 03 ("runs small" / "runs large"),
-- how many misfit reviews happen on them in the direction the tag warns about?
-- Those are the misfits a size tag is aimed at.
WITH item_stats AS (
    SELECT
        item_id,
        COUNT(*)                              AS reviews,
        COUNT(*) FILTER (WHERE fit = 'small') AS small_reviews,
        COUNT(*) FILTER (WHERE fit = 'large') AS large_reviews
    FROM reviews
    GROUP BY item_id
    HAVING COUNT(*) >= 30
),
flagged AS (
    -- same rule as query 03; "runs" holds the direction the item runs
    SELECT
        item_id,
        CASE
            WHEN small_reviews >= 0.25 * reviews AND small_reviews >= 2 * large_reviews THEN 'small'
            WHEN large_reviews >= 0.25 * reviews AND large_reviews >= 2 * small_reviews THEN 'large'
        END AS runs
    FROM item_stats
)
SELECT
    f.runs                                       AS flagged_as_running,
    COUNT(DISTINCT f.item_id)                    AS items,
    COUNT(*)                                     AS reviews,
    COUNT(*) FILTER (WHERE r.fit = f.runs)       AS misfits_in_flagged_direction,
    ROUND(100.0 * COUNT(*) FILTER (WHERE r.fit = f.runs) / COUNT(*), 1)  AS flagged_direction_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE r.fit = f.runs)
          / (SELECT COUNT(*) FROM reviews WHERE fit <> 'fit'), 1)       AS share_of_all_misfits_pct,
    ROUND(100.0 * COUNT(DISTINCT f.item_id)
          / (SELECT COUNT(DISTINCT item_id) FROM reviews), 1)            AS share_of_all_items_pct
FROM flagged f
JOIN reviews r ON r.item_id = f.item_id
WHERE f.runs IS NOT NULL
GROUP BY f.runs
ORDER BY f.runs DESC;
