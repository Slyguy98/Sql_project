DROP TABLE IF EXISTS player_metrics CASCADE;

CREATE TABLE player_metrics (
    metric_id SERIAL PRIMARY KEY,
    -- This MUST be appid to match the games table
    appid INT REFERENCES games(appid) ON DELETE CASCADE, 
    current_players INT NOT NULL,
    peak_24h INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);