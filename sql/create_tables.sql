-- 1. Player Demographics Table
CREATE TABLE IF NOT EXISTS players (
    player_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    nationality VARCHAR(50),
    age INTEGER,
    height_cm INTEGER,
    weight_kg INTEGER,
    preferred_foot VARCHAR(5), -- 'Left' or 'Right'
    injury_history TEXT,        -- Summary or Boolean indicator
    current_club VARCHAR(100),
    league_name VARCHAR(100) NOT NULL,
    position VARCHAR(20)        -- 'Goalkeeper', 'Defender', 'Midfielder', 'Forward'
);

-- 2. Outfield Player Seasonal Performance Table
CREATE TABLE IF NOT EXISTS outfield_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id VARCHAR(50),
    season VARCHAR(10) NOT NULL, -- e.g., '2023/2024'
    matches_played INTEGER DEFAULT 0,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    goal_contributions INTEGER DEFAULT 0, -- goals + assists
    shots INTEGER DEFAULT 0,
    tackles INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    aerial_duels_won_def INTEGER DEFAULT 0,
    aerial_duels_won_off INTEGER DEFAULT 0,
    avg_km_per_match REAL DEFAULT 0.0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- 3. Goalkeeper Seasonal Performance Table
CREATE TABLE IF NOT EXISTS goalkeeper_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id VARCHAR(50),
    season VARCHAR(10) NOT NULL,
    matches_played INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    big_saves INTEGER DEFAULT 0, -- Difficult saves
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);