"""
Test script to run SQL queries from sql/test_queries.sql
"""
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

from src.database import execute_query, get_connection, get_table_info

def run_test_queries():
    """Run all test queries from test_queries.sql"""
    
    print("\n" + "=" * 70)
    print("TESTING SQL QUERIES FROM test_queries.sql")
    print("=" * 70)
    
    # Test 1: Player counts grouped by league and position
    print("\n📊 TEST 1: Player Distribution by League and Position")
    print("-" * 50)
    query1 = """
    SELECT league_name, position, COUNT(*) as total_players
    FROM players
    GROUP BY league_name, position
    ORDER BY league_name, position
    """
    result1 = execute_query(query1)
    if result1:
        for row in result1:
            print(f"League: {row[0]:<25} | Position: {row[1]:<12} | Total: {row[2]}")
    else:
        print("No data found")
    
    # Test 2: Top 5 midfielders based on interceptions and distance
    print("\n🏃 TEST 2: Top 5 Midfielders by Interceptions and Distance")
    print("-" * 50)
    query2 = """
    SELECT p.name, p.current_club, s.season, s.interceptions, s.avg_km_per_match
    FROM players p
    JOIN outfield_stats s ON p.player_id = s.player_id
    WHERE p.position = 'Midfielder'
    ORDER BY s.interceptions DESC, s.avg_km_per_match DESC
    LIMIT 5
    """
    result2 = execute_query(query2)
    if result2:
        print(f"{'Player':<20} | {'Club':<20} | {'Season':<10} | {'Interceptions':<15} | {'Avg KM':<10}")
        print("-" * 80)
        for row in result2:
            print(f"{row[0]:<20} | {row[1]:<20} | {row[2]:<10} | {row[3]:<15} | {row[4]:<10}")
    else:
        print("No data found")
    
    # Test 3: Top goal scorers
    print("\n⚽ TEST 3: Top 10 Goal Scorers")
    print("-" * 50)
    query3 = """
    SELECT p.name, p.current_club, s.goals, s.assists, s.matches_played
    FROM players p
    JOIN outfield_stats s ON p.player_id = s.player_id
    WHERE p.position != 'Goalkeeper'
    ORDER BY s.goals DESC
    LIMIT 10
    """
    result3 = execute_query(query3)
    if result3:
        print(f"{'Player':<20} | {'Club':<20} | {'Goals':<8} | {'Assists':<8} | {'Matches':<10}")
        print("-" * 75)
        for row in result3:
            print(f"{row[0]:<20} | {row[1]:<20} | {row[2]:<8} | {row[3]:<8} | {row[4]:<10}")
    else:
        print("No data found")
    
    # Test 4: Best goalkeepers
    print("\n🧤 TEST 4: Top 5 Goalkeepers by Saves")
    print("-" * 50)
    query4 = """
    SELECT p.name, p.current_club, s.saves, s.goals_conceded, s.matches_played
    FROM players p
    JOIN goalkeeper_stats s ON p.player_id = s.player_id
    ORDER BY s.saves DESC
    LIMIT 5
    """
    result4 = execute_query(query4)
    if result4:
        print(f"{'Player':<20} | {'Club':<20} | {'Saves':<8} | {'Goals Conceded':<15} | {'Matches':<10}")
        print("-" * 80)
        for row in result4:
            print(f"{row[0]:<20} | {row[1]:<20} | {row[2]:<8} | {row[3]:<15} | {row[4]:<10}")
    else:
        print("No data found")
    
    # Test 5: League comparison
    print("\n🌍 TEST 5: League Statistics Comparison")
    print("-" * 50)
    query5 = """
    SELECT 
        league_name,
        COUNT(*) as players,
        ROUND(AVG(goals), 2) as avg_goals,
        ROUND(AVG(assists), 2) as avg_assists,
        ROUND(AVG(tackles), 2) as avg_tackles
    FROM players p
    JOIN outfield_stats s ON p.player_id = s.player_id
    WHERE p.position != 'Goalkeeper'
    GROUP BY league_name
    ORDER BY avg_goals DESC
    """
    result5 = execute_query(query5)
    if result5:
        print(f"{'League':<25} | {'Players':<8} | {'Avg Goals':<10} | {'Avg Assists':<12} | {'Avg Tackles':<12}")
        print("-" * 80)
        for row in result5:
            print(f"{row[0]:<25} | {row[1]:<8} | {row[2]:<10} | {row[3]:<12} | {row[4]:<12}")
    else:
        print("No data found")

def show_table_info():
    """Show schema information for all tables"""
    print("\n" + "=" * 70)
    print("DATABASE SCHEMA INFORMATION")
    print("=" * 70)
    
    tables = ['players', 'outfield_stats', 'goalkeeper_stats']
    
    for table in tables:
        print(f"\n📋 Table: {table}")
        print("-" * 50)
        columns = get_table_info(table)
        if columns:
            for col in columns:
                print(f"  {col[1]:<20} | {col[2]:<15} | Nullable: {not col[3]}")
        else:
            print(f"  Table '{table}' not found or empty")

if __name__ == "__main__":
    # Check if database exists
    from src.database import DB_PATH
    if DB_PATH.exists():
        print(f"✅ Database found at: {DB_PATH}")
        run_test_queries()
        show_table_info()
    else:
        print(f"⚠️ Database not found at: {DB_PATH}")
        print("Please run 'python main.py' first to populate the database.")