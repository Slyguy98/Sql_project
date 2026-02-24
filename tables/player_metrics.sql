DROP TABLE IF EXISTS player_metrics CASCADE;

CREATE TABLE player_metrics (
    metric_id SERIAL PRIMARY KEY,
    appid INT REFERENCES games(appid) ON DELETE CASCADE, 
    current_players INT NOT NULL,
    peak_24h INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);