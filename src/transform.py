"""
Data transformation module for football player statistics
"""
import pandas as pd
import json
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

def process_players_and_stats(raw_data: Dict) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Transform raw data into structured DataFrames
    
    Args:
        raw_data: Dictionary with player data
    
    Returns:
        Tuple of DataFrames (players, outfield_stats, goalkeeper_stats)
    """
    logger.info("Transforming data...")
    
    players_data = raw_data.get('players', [])
    
    if not players_data:
        logger.warning("No data to process")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # Separate players into categories
    outfield_players = []
    goalkeeper_players = []
    all_players = []
    
    for player in players_data:
        # Player demographics
        player_info = {
            'player_id': player.get('player_id'),
            'name': player.get('name'),
            'nationality': player.get('nationality'),
            'age': player.get('age'),
            'height_cm': player.get('height_cm'),
            'weight_kg': player.get('weight_kg'),
            'preferred_foot': player.get('preferred_foot'),
            'injury_history': player.get('injury_history', '[]'),
            'current_club': player.get('current_club'),
            'league_name': player.get('league_name'),
            'position': player.get('position')
        }
        all_players.append(player_info)
        
        if player.get('is_goalkeeper', False):
            # Goalkeeper stats
            gk_stats = {
                'player_id': player.get('player_id'),
                'season': player.get('season'),
                'matches_played': player.get('matches_played', 0),
                'goals_conceded': player.get('goals_conceded', 0),
                'saves': player.get('saves', 0),
                'big_saves': player.get('big_saves', 0),
                'yellow_cards': player.get('yellow_cards', 0),
                'red_cards': player.get('red_cards', 0)
            }
            goalkeeper_players.append(gk_stats)
        else:
            # Outfield stats
            outfield_stats = {
                'player_id': player.get('player_id'),
                'season': player.get('season'),
                'matches_played': player.get('matches_played', 0),
                'goals': player.get('goals', 0),
                'assists': player.get('assists', 0),
                'goal_contributions': player.get('goal_contributions', 0),
                'shots': player.get('shots', 0),
                'tackles': player.get('tackles', 0),
                'interceptions': player.get('interceptions', 0),
                'aerial_duels_won_def': player.get('aerial_duels_won_def', 0),
                'aerial_duels_won_off': player.get('aerial_duels_won_off', 0),
                'avg_km_per_match': player.get('avg_km_per_match', 0.0),
                'yellow_cards': player.get('yellow_cards', 0),
                'red_cards': player.get('red_cards', 0)
            }
            outfield_players.append(outfield_stats)
    
    # Create DataFrames
    df_players = pd.DataFrame(all_players)
    df_outfield = pd.DataFrame(outfield_players)
    df_goalkeeper = pd.DataFrame(goalkeeper_players)
    
    # Remove duplicates
    df_players = df_players.drop_duplicates(subset=['player_id'])
    df_outfield = df_outfield.drop_duplicates(subset=['player_id', 'season'])
    df_goalkeeper = df_goalkeeper.drop_duplicates(subset=['player_id', 'season'])
    
    logger.info(f"Processed {len(df_players)} players")
    logger.info(f"Processed {len(df_outfield)} outfield player records")
    logger.info(f"Processed {len(df_goalkeeper)} goalkeeper records")
    
    return df_players, df_outfield, df_goalkeeper

def calculate_advanced_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate advanced metrics for outfield players
    """
    # Goal efficiency (goals per shot)
    df['goal_efficiency'] = df.apply(
        lambda row: row['goals'] / row['shots'] if row['shots'] > 0 else 0,
        axis=1
    )
    
    # Goals per match
    df['goals_per_match'] = df.apply(
        lambda row: row['goals'] / row['matches_played'] if row['matches_played'] > 0 else 0,
        axis=1
    )
    
    # Assists per match
    df['assists_per_match'] = df.apply(
        lambda row: row['assists'] / row['matches_played'] if row['matches_played'] > 0 else 0,
        axis=1
    )
    
    # Defensive actions per match
    df['defensive_actions_per_match'] = df.apply(
        lambda row: (row['tackles'] + row['interceptions']) / row['matches_played'] 
        if row['matches_played'] > 0 else 0,
        axis=1
    )
    
    return df