DROP TABLE IF EXISTS games CASCADE;

CREATE TABLE games (
    appid INT PRIMARY KEY,
    title TEXT,
    release_date DATE,
    english INT,
    developer TEXT,
    publisher TEXT,
    platforms TEXT,
    required_age INT,
    categories TEXT, -- We keep these for the initial import
    genres TEXT,     -- We keep these for the initial import
    steamspy_tags TEXT,
    achievements INT,
    positive_ratings INT,
    negative_ratings INT,
    average_playtime INT,
    median_playtime INT,
    owners TEXT,
    price DECIMAL(10, 2),
    -- Pre-calculates the score for the dashboard
    rating_pct FLOAT GENERATED ALWAYS AS (
        CASE WHEN (positive_ratings + negative_ratings) > 0 
        THEN (positive_ratings::float / (positive_ratings + negative_ratings) * 100) 
        ELSE 0 END
    ) STORED
);