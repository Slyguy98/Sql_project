DROP TABLE IF EXISTS genres CASCADE;

CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);