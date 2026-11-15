-- How many reviews say the item fit, ran small or ran large?
-- A "misfit" is any review where fit is 'small' or 'large'.
-- COUNT(*) FILTER (WHERE ...) counts only the rows that match the condition.
SELECT
    COUNT(*)                                     AS reviews,
    COUNT(*) FILTER (WHERE fit = 'fit')          AS fit_reviews,
    COUNT(*) FILTER (WHERE fit = 'small')        AS small_reviews,
    COUNT(*) FILTER (WHERE fit = 'large')        AS large_reviews,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit <> 'fit')  / COUNT(*), 1) AS misfit_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit = 'small') / COUNT(*), 1) AS small_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit = 'large') / COUNT(*), 1) AS large_pct
FROM reviews;
