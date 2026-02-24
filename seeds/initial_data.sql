-- Active: 1770524401552@@localhost@5432@postgres
-- Step 1: Clean the slate (Optional: prevents duplicate errors if you run this twice)
TRUNCATE player_metrics, games, genres RESTART IDENTITY CASCADE;

-- Step 2: Insert Genres first (The "Parents")
INSERT INTO genres (genre_name, description) VALUES 
('FPS', 'First-Person Shooters focusing on gunplay.'),
('MOBA', 'Multiplayer Online Battle Arenas.'),
('RPG', 'Role-Playing Games with deep stories.'),
('Battle Royale', 'Last man standing survival games.');

-- Step 3: Insert Games (The "Children" - linking to genres)
INSERT INTO games (title, game_type, genre_id) VALUES 
('Valorant', 'Multiplayer', (SELECT genre_id FROM genres WHERE genre_name = 'FPS')),
('League of Legends', 'Multiplayer', (SELECT genre_id FROM genres WHERE genre_name = 'MOBA')),
('Elden Ring', 'Single Player', (SELECT genre_id FROM genres WHERE genre_name = 'RPG')),
('Fortnite', 'Multiplayer', (SELECT genre_id FROM genres WHERE genre_name = 'Battle Royale'));

-- Step 4: Insert Metrics (The "Grandchildren" - linking to games)
INSERT INTO player_metrics (game_id, current_players, peak_24h) VALUES 
((SELECT game_id FROM games WHERE title = 'Valorant'), 750000, 1100000),
((SELECT game_id FROM games WHERE title = 'League of Legends'), 2100000, 3800000),
((SELECT game_id FROM games WHERE title = 'Elden Ring'), 62000, 150000),
((SELECT game_id FROM games WHERE title = 'Fortnite'), 1800000, 4000000);