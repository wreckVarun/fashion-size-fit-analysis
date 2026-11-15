-- Misfit rate by category, for categories with at least 500 reviews.
SELECT
    category,
    COUNT(*)                                AS reviews,
    COUNT(*) FILTER (WHERE fit <> 'fit')    AS misfit_reviews,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit <> 'fit')  / COUNT(*), 1) AS misfit_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit = 'small') / COUNT(*), 1) AS small_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit = 'large') / COUNT(*), 1) AS large_pct
FROM reviews
GROUP BY category
HAVING COUNT(*) >= 500
ORDER BY misfit_pct DESC;
