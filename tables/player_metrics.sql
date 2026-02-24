CREATE TABLE player_metrics (
    metric_id SERIAL PRIMARY KEY,
    game_id INT REFERENCES games(game_id) ON DELETE CASCADE,
    current_players INT NOT NULL,
    peak_24h INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);