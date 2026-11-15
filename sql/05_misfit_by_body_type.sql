-- Misfit rate by the body type the reviewer chose for their profile.
-- Reviews with no body type are shown as 'not given'.
SELECT
    COALESCE(body_type, 'not given') AS body_type,
    COUNT(*)                         AS reviews,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit <> 'fit')  / COUNT(*), 1) AS misfit_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit = 'small') / COUNT(*), 1) AS small_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fit = 'large') / COUNT(*), 1) AS large_pct
FROM reviews
GROUP BY 1
ORDER BY misfit_pct DESC;
