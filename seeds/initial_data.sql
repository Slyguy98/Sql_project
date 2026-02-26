TRUNCATE games, genres, game_genres, categories, game_categories, player_metrics RESTART IDENTITY CASCADE;

-- Step 1: Import CSV
\copy games FROM '/home/jamil/sql_project/seeds/steam.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Step 2: Extract Genres
INSERT INTO genres (genre_name) 
SELECT DISTINCT unnest(string_to_array(genres, ';')) FROM games ON CONFLICT DO NOTHING;

INSERT INTO game_genres (appid, genre_id)
SELECT g.appid, gn.genre_id
FROM games g
CROSS JOIN LATERAL unnest(string_to_array(g.genres, ';')) AS s(name)
JOIN genres gn ON gn.genre_name = s.name ON CONFLICT DO NOTHING;

-- Step 3: Extract Categories (Multi-player, etc.)
INSERT INTO categories (category_name) 
SELECT DISTINCT unnest(string_to_array(categories, ';')) FROM games ON CONFLICT DO NOTHING;

INSERT INTO game_categories (appid, category_id)
SELECT g.appid, c.category_id
FROM games g
CROSS JOIN LATERAL unnest(string_to_array(g.categories, ';')) AS s(name)
JOIN categories c ON c.category_name = s.name ON CONFLICT DO NOTHING;