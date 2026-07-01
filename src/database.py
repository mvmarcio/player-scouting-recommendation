"""
Database module for football player scouting system
"""
import sqlite3
import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database path from .env or use default
DB_PATH = Path(os.getenv('DB_PATH', 'data/scouting_database.db'))

def get_connection():
    """Return a connection to the SQLite database"""
    # Ensure directory exists
    os.makedirs(DB_PATH.parent, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def initialize_database():
    """Initialize database tables with the specified schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Player Demographics Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        player_id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        nationality VARCHAR(50),
        age INTEGER,
        height_cm INTEGER,
        weight_kg INTEGER,
        preferred_foot VARCHAR(5),
        injury_history TEXT,
        current_club VARCHAR(100),
        league_name VARCHAR(100) NOT NULL,
        position VARCHAR(20)
    )
    ''')
    
    # 2. Outfield Player Seasonal Performance Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS outfield_stats (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id VARCHAR(50),
        season VARCHAR(10) NOT NULL,
        matches_played INTEGER DEFAULT 0,
        goals INTEGER DEFAULT 0,
        assists INTEGER DEFAULT 0,
        goal_contributions INTEGER DEFAULT 0,
        shots INTEGER DEFAULT 0,
        tackles INTEGER DEFAULT 0,
        interceptions INTEGER DEFAULT 0,
        aerial_duels_won_def INTEGER DEFAULT 0,
        aerial_duels_won_off INTEGER DEFAULT 0,
        avg_km_per_match REAL DEFAULT 0.0,
        yellow_cards INTEGER DEFAULT 0,
        red_cards INTEGER DEFAULT 0,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    )
    ''')
    
    # 3. Goalkeeper Seasonal Performance Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goalkeeper_stats (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id VARCHAR(50),
        season VARCHAR(10) NOT NULL,
        matches_played INTEGER DEFAULT 0,
        goals_conceded INTEGER DEFAULT 0,
        saves INTEGER DEFAULT 0,
        big_saves INTEGER DEFAULT 0,
        yellow_cards INTEGER DEFAULT 0,
        red_cards INTEGER DEFAULT 0,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_league ON players(league_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_position ON players(position)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_name ON players(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_outfield_player_season ON outfield_stats(player_id, season)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_goalkeeper_player_season ON goalkeeper_stats(player_id, season)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_outfield_season ON outfield_stats(season)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_goalkeeper_season ON goalkeeper_stats(season)')
    
    conn.commit()
    conn.close()
    logger.info(f"Database tables created/verified successfully at {DB_PATH}!")

def clear_database():
    """Clear all tables (useful for testing)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM goalkeeper_stats')
    cursor.execute('DELETE FROM outfield_stats')
    cursor.execute('DELETE FROM players')
    conn.commit()
    conn.close()
    logger.info("Database cleared!")
    
def get_player_count():
    """Get total number of players in database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM players')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_stats_count():
    """Get total number of stats records in database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM outfield_stats')
    outfield_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM goalkeeper_stats')
    goalkeeper_count = cursor.fetchone()[0]
    conn.close()
    return outfield_count + goalkeeper_count

def execute_query(query, params=None):
    """Execute a raw SQL query (for testing)"""
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    # Check if it's a SELECT query
    if query.strip().upper().startswith('SELECT'):
        results = cursor.fetchall()
        conn.close()
        return results
    else:
        conn.commit()
        conn.close()
        return None

def get_table_info(table_name):
    """Get table schema information"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    conn.close()
    return columns