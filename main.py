"""
Football Player Scouting and Recommendation System
Main pipeline execution
"""
import sys
import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add root directory to path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

from src.database import initialize_database, get_connection, get_player_count, get_stats_count, clear_database
from src.extract import FootballDataExtractor
from src.transform import process_players_and_stats
from src.recommend import PlayerRecommender

def main():
    logger.info("=" * 60)
    logger.info("FOOTBALL PLAYER SCOUTING RECOMMENDATION SYSTEM")
    logger.info("=" * 60)
    
    try:
        # 1. Initialize database
        logger.info("Step 1: Initializing database...")
        initialize_database()
        
        # 2. Extract data
        logger.info("Step 2: Extracting data...")
        extractor = FootballDataExtractor()
        
        # Define leagues to extract
        # You can add more leagues from the list
        leagues = [
            71,  # Brasileirão Série A
            72,  # Brasileirão Série B
            73,  # Brasileirão Série C
        ]
        
        seasons = [2026]  # Most recent season
        
        # For testing, use limited data
        test_leagues = [71]  # Only Brazil Serie A
        all_data = extractor.fetch_multiple_leagues(test_leagues, seasons)
        
        players_extracted = len(all_data.get('players', []))
        logger.info(f"Extracted {players_extracted} player records")
        
        # 3. Transform data
        logger.info("Step 3: Transforming data...")
        df_players, df_outfield, df_goalkeeper = process_players_and_stats(all_data)
        
        # 4. Load data to database
        logger.info("Step 4: Loading data to database...")
        conn = get_connection()
        
        if not df_players.empty:
            # Load players
            df_players.to_sql('players', conn, if_exists='append', index=False)
            logger.info(f"✅ Loaded {len(df_players)} players")
            
            # Load outfield stats
            if not df_outfield.empty:
                df_outfield.to_sql('outfield_stats', conn, if_exists='append', index=False)
                logger.info(f"✅ Loaded {len(df_outfield)} outfield player records")
            
            # Load goalkeeper stats
            if not df_goalkeeper.empty:
                df_goalkeeper.to_sql('goalkeeper_stats', conn, if_exists='append', index=False)
                logger.info(f"✅ Loaded {len(df_goalkeeper)} goalkeeper records")
            
            conn.close()
            
            # 5. Show summary
            logger.info("=" * 60)
            logger.info("Step 5: Pipeline completed successfully!")
            logger.info(f"📊 Total players in database: {get_player_count()}")
            logger.info(f"📊 Total stats records: {get_stats_count()}")
            
            # 6. Test the SQL queries
            logger.info("=" * 60)
            logger.info("Step 6: Running SQL test queries...")
            run_sql_tests()
            
            # 7. Test recommendation system
            logger.info("=" * 60)
            logger.info("Step 7: Testing recommendation system...")
            test_recommendations()
            
        else:
            logger.warning("No data to save!")
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

def run_sql_tests():
    """Run SQL test queries"""
    from src.database import execute_query
    
    print("\n" + "=" * 60)
    print("SQL QUERY TESTS")
    print("=" * 60)
    
    # Test 1: Player counts by league and position
    query1 = """
    SELECT league_name, position, COUNT(*) as total_players
    FROM players
    GROUP BY league_name, position
    ORDER BY league_name, position
    """
    result1 = execute_query(query1)
    if result1:
        print("\n📊 Player Distribution by League and Position:")
        print("-" * 50)
        for row in result1[:10]:  # Show first 10
            print(f"League: {row[0]:<25} | Position: {row[1]:<12} | Total: {row[2]}")
    
    # Test 2: Top scorers
    query2 = """
    SELECT p.name, p.current_club, s.goals, s.assists
    FROM players p
    JOIN outfield_stats s ON p.player_id = s.player_id
    WHERE p.position != 'Goalkeeper'
    ORDER BY s.goals DESC
    LIMIT 5
    """
    result2 = execute_query(query2)
    if result2:
        print("\n⚽ Top 5 Goal Scorers:")
        print("-" * 50)
        print(f"{'Player':<20} | {'Club':<20} | {'Goals':<8} | {'Assists':<8}")
        print("-" * 60)
        for row in result2:
            print(f"{row[0]:<20} | {row[1]:<20} | {row[2]:<8} | {row[3]:<8}")

def test_recommendations():
    """Test the recommendation system"""
    try:
        recommender = PlayerRecommender()
        
        print("\n" + "=" * 60)
        print("RECOMMENDATION SYSTEM TESTS")
        print("=" * 60)
        
        # Check if there are players
        if recommender.get_player_count() == 0:
            print("⚠️ No players in database to recommend")
            return
        
        # Top scorers
        print("\n⚽ Top 5 Goal Scorers:")
        top_scorers = recommender.get_top_scorers()
        if not top_scorers.empty:
            print(top_scorers[['name', 'current_club', 'goals', 'matches_played']].to_string(index=False))
        
        # Top midfielders
        print("\n🎯 Top 5 Midfielders by Interceptions:")
        top_midfielders = recommender.get_top_midfielders()
        if not top_midfielders.empty:
            print(top_midfielders[['name', 'current_club', 'interceptions', 'avg_km_per_match']].to_string(index=False))
        
        # Top defenders
        print("\n🛡️ Top 5 Defenders by Tackles:")
        top_defenders = recommender.get_top_defenders()
        if not top_defenders.empty:
            print(top_defenders[['name', 'current_club', 'tackles', 'interceptions']].to_string(index=False))
        
        # Position-based recommendation
        print("\n🧤 Recommended Goalkeepers:")
        gk_recommendations = recommender.recommend_by_position('Goalkeeper', top_n=3)
        if not gk_recommendations.empty:
            print(gk_recommendations.to_string(index=False))
        
        # Similar players (if there are at least 2 players)
        if len(recommender.players_df) >= 2:
            first_player_id = recommender.players_df['player_id'].iloc[0]
            print(f"\n👥 Finding similar players to {recommender.players_df['name'].iloc[0]}...")
            similar = recommender.find_similar_players(first_player_id)
            if not similar.empty:
                print(similar[['name', 'current_club', 'position', 'distance']].to_string(index=False))
        
    except Exception as e:
        logger.error(f"Error testing recommendations: {e}")

if __name__ == "__main__":
    main()