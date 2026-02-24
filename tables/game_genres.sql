DROP TABLE IF EXISTS game_genres CASCADE;

CREATE TABLE game_genres (
    appid INT REFERENCES games(appid) ON DELETE CASCADE,
    genre_id INT REFERENCES genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (appid, genre_id)
);