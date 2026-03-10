CREATE OR REPLACE VIEW publisher_outcomes AS
WITH raw_stats AS (
    SELECT 
        publisher,
        COUNT(appid) as total_titles,
        -- Calculate midpoint of owners '10000-20000' -> 15000
        AVG((split_part(owners, '-', 1)::NUMERIC + split_part(owners, '-', 2)::NUMERIC) / 2) as avg_owner_base,
        SUM((split_part(owners, '-', 1)::NUMERIC + split_part(owners, '-', 2)::NUMERIC) / 2) as total_estimated_owners,
        AVG(price) as avg_price,
        SUM(price * ((split_part(owners, '-', 1)::NUMERIC + split_part(owners, '-', 2)::NUMERIC) / 2)) as est_gross_revenue,
        AVG(average_playtime / 60.0) as avg_hours_per_game,
        AVG(rating_pct) as avg_approval
    FROM games
    GROUP BY publisher
)
SELECT 
    publisher,
    total_titles,
    ROUND(total_estimated_owners, 0) as total_owners,
    ROUND(est_gross_revenue, 2) as total_revenue,
    ROUND(avg_hours_per_game, 1) as engagement_score,
    ROUND(avg_approval, 2) as satisfaction_score,
    -- Labeling them to see "All Data" but filter easily
    CASE 
        WHEN est_gross_revenue > 100000000 THEN 'Tier 1: Global Giant'
        WHEN est_gross_revenue > 10000000 THEN 'Tier 2: Major'
        WHEN est_gross_revenue > 1000000 THEN 'Tier 3: Mid-Market'
        ELSE 'Tier 4: Small/Indie'
    END as market_tier
FROM raw_stats
ORDER BY total_revenue DESC;