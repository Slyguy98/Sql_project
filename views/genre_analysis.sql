CREATE OR REPLACE VIEW genre_analysis AS
WITH split_genres AS (
    -- This "unnests" the semicolon list into individual rows
    SELECT 
        unnest(string_to_array(genres, ';')) as genre,
        positive_ratings,
        negative_ratings,
        average_playtime
    FROM games
)
SELECT 
    genre,
    COUNT(*) as total_games,
    SUM(positive_ratings) as total_positives,
    ROUND(AVG(average_playtime), 2) as avg_playtime_mins,
    -- Calculate the "Appeal Score" (Percentage of positive ratings)
    ROUND(SUM(positive_ratings)::numeric / (NULLIF(SUM(positive_ratings) + SUM(negative_ratings), 0)) * 100, 2) as approval_rating
FROM split_genres
GROUP BY genre
ORDER BY total_games DESC;