DROP TABLE IF EXISTS categories CASCADE;
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS game_categories CASCADE;
CREATE TABLE game_categories (
    appid INT REFERENCES games(appid) ON DELETE CASCADE,
    category_id INT REFERENCES categories(category_id) ON DELETE CASCADE,
    PRIMARY KEY (appid, category_id)
);