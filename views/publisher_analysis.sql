CREATE OR REPLACE VIEW publisher_outcomes AS
-- Added CTE to split semicolon-separated publishers into individual rows
WITH exploded_data AS (
    SELECT 
        trim(unnest(string_to_array(publisher, ';'))) as individual_publisher,
        owners,
        price,
        average_playtime,
        rating_pct,
        appid
    FROM games
    WHERE publisher IS NOT NULL AND publisher != ''
),
raw_stats AS (
    SELECT 
    -- Grouping by the new individual names instead of the messy strings
        individual_publisher as publisher,
        COUNT(appid) as total_titles,
        -- Calculate midpoint of owners '10000-20000' -> 15000
        AVG((split_part(owners, '-', 1)::NUMERIC + split_part(owners, '-', 2)::NUMERIC) / 2) as avg_owner_base,
        SUM((split_part(owners, '-', 1)::NUMERIC + split_part(owners, '-', 2)::NUMERIC) / 2) as total_estimated_owners,
        AVG(price) as avg_price,
        SUM(price * ((split_part(owners, '-', 1)::NUMERIC + split_part(owners, '-', 2)::NUMERIC) / 2)) as est_gross_revenue,
        AVG(average_playtime / 60.0) as avg_hours_per_game,
        AVG(rating_pct) as avg_approval
    FROM exploded_data
    GROUP BY publisher
)
SELECT 
    publisher,
    total_titles,
    ROUND(total_estimated_owners::NUMERIC, 0) as total_owners,
    ROUND(est_gross_revenue::NUMERIC, 2) as total_revenue,
    ROUND(avg_hours_per_game::NUMERIC, 1) as engagement_score,
    ROUND(avg_approval::NUMERIC, 2) as satisfaction_score,
    -- Labeling them to see "All Data" but filter easily
    CASE 
        WHEN est_gross_revenue > 100000000 THEN 'Tier 1: Global Giant'
        WHEN est_gross_revenue > 10000000 THEN 'Tier 2: Major'
        WHEN est_gross_revenue > 1000000 THEN 'Tier 3: Mid-Market'
        ELSE 'Tier 4: Small/Indie'
    END as market_tier
FROM raw_stats
ORDER BY total_revenue DESC;