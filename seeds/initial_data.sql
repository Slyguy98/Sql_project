-- Step 1: Bulk Load the 27k games from the CSV
-- Note: This assumes steam.csv is in your seeds folder
TRUNCATE games, genres, game_genres, player_metrics RESTART IDENTITY CASCADE;

\copy games FROM '/home/jamil/sql_project/seeds/steam.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Step 2: Automatically Populate the Relational Tables
-- This extracts the unique genres and builds the Many-to-Many links
INSERT INTO genres (genre_name) 
SELECT DISTINCT unnest(string_to_array(genres, ';')) FROM games 
ON CONFLICT DO NOTHING;

INSERT INTO game_genres (appid, genre_id)
SELECT g.appid, gn.genre_id
FROM games g
CROSS JOIN LATERAL unnest(string_to_array(g.genres, ';')) AS s(name)
JOIN genres gn ON gn.genre_name = s.name 
ON CONFLICT DO NOTHING;