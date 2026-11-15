-- Do misfits get lower ratings? Ratings are 1-5 stars.
SELECT
    fit,
    COUNT(*)              AS reviews,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(100.0 * COUNT(*) FILTER (WHERE rating = 5)  / COUNT(*), 1) AS five_star_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE rating <= 3) / COUNT(*), 1) AS three_or_less_pct
FROM reviews
GROUP BY fit
ORDER BY avg_rating DESC;
