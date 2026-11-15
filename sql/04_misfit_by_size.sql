-- Misfit rate by the size that was ordered.
-- RentTheRunway stores size as a number code (0-58). We keep the main sizes,
-- those with at least 3,000 reviews, so each rate rests on plenty of data.
-- reviews_pct shows how much of all reviews each size covers.
SELECT
    size,
    COUNT(*) AS reviews,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM reviews), 1)        AS reviews_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit <> 'fit')  / COUNT(*), 1) AS misfit_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit = 'small') / COUNT(*), 1) AS small_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit = 'large') / COUNT(*), 1) AS large_pct
FROM reviews
GROUP BY size
HAVING COUNT(*) >= 3000
ORDER BY size;
