-- Which items "run small" or "run large"?
-- We only judge items with 30+ reviews. An item is flagged when:
--   * at least 25% of its reviews say small (or large), which is about double
--     the site-wide rate of roughly 13%, and
--   * that direction has at least twice as many reviews as the other one.
WITH item_stats AS (
    SELECT
        item_id,
        MIN(category)                           AS category,
        COUNT(*)                                AS reviews,
        COUNT(*) FILTER (WHERE fit = 'small')   AS small_reviews,
        COUNT(*) FILTER (WHERE fit = 'large')   AS large_reviews,
        ROUND(AVG(rating), 2)                   AS avg_rating
    FROM reviews
    GROUP BY item_id
    HAVING COUNT(*) >= 30
)
SELECT
    item_id,
    category,
    reviews,
    small_reviews,
    large_reviews,
    ROUND(100.0 * small_reviews / reviews, 1) AS small_pct,
    ROUND(100.0 * large_reviews / reviews, 1) AS large_pct,
    avg_rating,
    CASE
        WHEN small_reviews >= 0.25 * reviews AND small_reviews >= 2 * large_reviews THEN 'runs small'
        WHEN large_reviews >= 0.25 * reviews AND large_reviews >= 2 * small_reviews THEN 'runs large'
        ELSE 'not flagged'
    END AS flag
FROM item_stats
ORDER BY reviews DESC;
