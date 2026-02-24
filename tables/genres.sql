-- Step 1: Wipe the old table if it exists
DROP TABLE IF EXISTS genres CASCADE;

-- Step 2: Create the fresh table
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);