CREATE OR REPLACE VIEW category_analysis AS
SELECT 
    c.category_name as category,
    COUNT(g.appid) as total_games,
    ROUND(AVG(g.rating_pct)::numeric, 2) as avg_approval
FROM categories c
JOIN game_categories gc ON c.category_id = gc.category_id
JOIN games g ON gc.appid = g.appid
GROUP BY c.category_name
ORDER BY total_games DESC;