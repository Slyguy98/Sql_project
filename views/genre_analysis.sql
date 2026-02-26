DROP VIEW IF EXISTS genre_analysis CASCADE;
CREATE OR REPLACE VIEW genre_analysis AS
SELECT 
    gn.genre_name as genre,
    COUNT(g.appid) as total_games,
    ROUND(AVG(g.rating_pct)::numeric, 2) as approval_rating
FROM genres gn
JOIN game_genres gg ON gn.genre_id = gg.genre_id
JOIN games g ON gg.appid = g.appid
GROUP BY gn.genre_name
HAVING COUNT(g.appid) > 50
ORDER BY total_games DESC;