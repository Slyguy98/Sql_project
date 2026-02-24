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
    categories TEXT,
    genres TEXT,
    steamspy_tags TEXT,
    achievements INT,
    positive_ratings INT,
    negative_ratings INT,
    average_playtime INT,
    median_playtime INT,
    owners TEXT,
    price DECIMAL(10, 2)
);