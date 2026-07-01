"""
Recommendation system for football player scouting
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from src.database import get_connection
import logging

logger = logging.getLogger(__name__)

class PlayerRecommender:
    """
    Player recommendation system based on characteristics and statistics
    """
    
    def __init__(self):
        self.conn = get_connection()
        self.load_data()
    
    def load_data(self):
        """Load data from database into DataFrames"""
        try:
            # Load players
            self.players_df = pd.read_sql_query("SELECT * FROM players", self.conn)
            
            # Load outfield stats (latest season)
            self.outfield_df = pd.read_sql_query("""
                SELECT * FROM outfield_stats 
                WHERE season = (SELECT MAX(season) FROM outfield_stats)
            """, self.conn)
            
            # Load goalkeeper stats (latest season)
            self.goalkeeper_df = pd.read_sql_query("""
                SELECT * FROM goalkeeper_stats 
                WHERE season = (SELECT MAX(season) FROM goalkeeper_stats)
            """, self.conn)
            
            # Merge data for easier access
            self.full_df = pd.merge(
                self.players_df, 
                self.outfield_df, 
                on='player_id', 
                how='left'
            )
            
            logger.info(f"Loaded {len(self.players_df)} players, {len(self.outfield_df)} outfield stats, {len(self.goalkeeper_df)} goalkeeper stats")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.players_df = pd.DataFrame()
            self.outfield_df = pd.DataFrame()
            self.goalkeeper_df = pd.DataFrame()
            self.full_df = pd.DataFrame()
    
    def get_player_count(self) -> int:
        """Get total number of players"""
        return len(self.players_df)
    
    def get_top_scorers(self, min_games: int = 10, top_n: int = 10) -> pd.DataFrame:
        """Get top goal scorers from outfield players"""
        df = self.outfield_df[self.outfield_df['matches_played'] >= min_games]
        df = pd.merge(df, self.players_df[['player_id', 'name', 'current_club', 'position']], on='player_id')
        return df.nlargest(top_n, 'goals')
    
    def get_top_assists(self, min_games: int = 10, top_n: int = 10) -> pd.DataFrame:
        """Get top assist providers from outfield players"""
        df = self.outfield_df[self.outfield_df['matches_played'] >= min_games]
        df = pd.merge(df, self.players_df[['player_id', 'name', 'current_club', 'position']], on='player_id')
        return df.nlargest(top_n, 'assists')
    
    def get_top_midfielders(self, min_games: int = 10, top_n: int = 10) -> pd.DataFrame:
        """Get top midfielders based on interceptions and distance"""
        df = self.outfield_df[self.outfield_df['matches_played'] >= min_games]
        df = pd.merge(df, self.players_df[['player_id', 'name', 'current_club', 'position']], on='player_id')
        df = df[df['position'] == 'Midfielder']
        df['score'] = df['interceptions'] * 0.6 + df['avg_km_per_match'] * 0.4
        return df.nlargest(top_n, 'score')
    
    def get_top_defenders(self, min_games: int = 10, top_n: int = 10) -> pd.DataFrame:
        """Get top defenders based on tackles and interceptions"""
        df = self.outfield_df[self.outfield_df['matches_played'] >= min_games]
        df = pd.merge(df, self.players_df[['player_id', 'name', 'current_club', 'position']], on='player_id')
        df = df[df['position'] == 'Defender']
        df['score'] = df['tackles'] * 0.5 + df['interceptions'] * 0.3 + df['aerial_duels_won_def'] * 0.2
        return df.nlargest(top_n, 'score')
    
    def get_top_goalkeepers(self, min_games: int = 10, top_n: int = 10) -> pd.DataFrame:
        """Get top goalkeepers based on saves"""
        df = self.goalkeeper_df[self.goalkeeper_df['matches_played'] >= min_games]
        df = pd.merge(df, self.players_df[['player_id', 'name', 'current_club']], on='player_id')
        df['save_ratio'] = df['saves'] / df['goals_conceded'].replace(0, 1)
        return df.nlargest(top_n, 'saves')
    
    def recommend_by_position(self, position: str, top_n: int = 10) -> pd.DataFrame:
        """Recommend players by position"""
        df = self.players_df[self.players_df['position'] == position]
        
        # Add stats based on position
        if position == 'Goalkeeper':
            df = pd.merge(df, self.goalkeeper_df, on='player_id', how='inner')
            df['score'] = df['saves'] * 0.6 - df['goals_conceded'] * 0.4
            return df.nlargest(top_n, 'score')[['name', 'current_club', 'saves', 'goals_conceded', 'matches_played']]
        elif position == 'Defender':
            df = pd.merge(df, self.outfield_df, on='player_id', how='inner')
            df['score'] = df['tackles'] * 0.4 + df['interceptions'] * 0.4 + df['aerial_duels_won_def'] * 0.2
            return df.nlargest(top_n, 'score')[['name', 'current_club', 'tackles', 'interceptions', 'matches_played']]
        elif position == 'Midfielder':
            df = pd.merge(df, self.outfield_df, on='player_id', how='inner')
            df['score'] = df['assists'] * 0.4 + df['interceptions'] * 0.3 + df['avg_km_per_match'] * 0.3
            return df.nlargest(top_n, 'score')[['name', 'current_club', 'assists', 'interceptions', 'avg_km_per_match']]
        elif position == 'Forward':
            df = pd.merge(df, self.outfield_df, on='player_id', how='inner')
            df['score'] = df['goals'] * 0.6 + df['assists'] * 0.3 + df['shots'] * 0.1
            return df.nlargest(top_n, 'score')[['name', 'current_club', 'goals', 'assists', 'shots']]
        else:
            return pd.DataFrame()
    
    def recommend_by_stats(self, criteria: Dict[str, float], top_n: int = 10) -> pd.DataFrame:
        """
        Recommend players based on statistical criteria
        
        Args:
            criteria: Dictionary with column names and minimum values
            Example: {'goals': 5, 'assists': 3, 'matches_played': 20}
        """
        df = self.outfield_df.copy()
        
        for col, min_value in criteria.items():
            if col in df.columns:
                df = df[df[col] >= min_value]
        
        df = pd.merge(df, self.players_df[['player_id', 'name', 'current_club', 'position']], on='player_id')
        return df.head(top_n)
    
    def find_similar_players(self, player_id: str, top_n: int = 5) -> pd.DataFrame:
        """
        Find similar players using Euclidean distance
        """
        # Get target player
        target = self.players_df[self.players_df['player_id'] == player_id]
        
        if target.empty:
            logger.warning(f"Player {player_id} not found")
            return pd.DataFrame()
        
        target_position = target['position'].iloc[0]
        
        if target_position == 'Goalkeeper':
            return self._find_similar_goalkeeper(player_id, top_n)
        else:
            return self._find_similar_outfield(player_id, top_n)
    
    def _find_similar_outfield(self, player_id: str, top_n: int) -> pd.DataFrame:
        """Find similar outfield players"""
        # Get target stats
        target_stats = self.outfield_df[self.outfield_df['player_id'] == player_id]
        if target_stats.empty:
            return pd.DataFrame()
        
        # Features for similarity
        features = ['goals', 'assists', 'tackles', 'interceptions', 'avg_km_per_match']
        target_features = target_stats[features].iloc[0].values
        
        # Find other players with same position
        target_position = self.players_df[self.players_df['player_id'] == player_id]['position'].iloc[0]
        same_position = self.players_df[self.players_df['position'] == target_position]['player_id'].tolist()
        
        # Filter out target
        same_position = [pid for pid in same_position if pid != player_id]
        
        if not same_position:
            return pd.DataFrame()
        
        # Get stats for same position players
        other_stats = self.outfield_df[self.outfield_df['player_id'].isin(same_position)]
        
        if other_stats.empty:
            return pd.DataFrame()
        
        # Calculate distances
        distances = []
        for _, row in other_stats.iterrows():
            dist = np.sqrt(sum((row[f] - target_features[i])**2 for i, f in enumerate(features)))
            distances.append(dist)
        
        other_stats['distance'] = distances
        other_stats = other_stats.sort_values('distance')
        
        # Merge with player info
        result = pd.merge(
            other_stats.head(top_n),
            self.players_df[['player_id', 'name', 'current_club', 'position']],
            on='player_id'
        )
        
        return result[['name', 'current_club', 'position', 'goals', 'assists', 'tackles', 'interceptions', 'distance']]
    
    def _find_similar_goalkeeper(self, player_id: str, top_n: int) -> pd.DataFrame:
        """Find similar goalkeepers"""
        target_stats = self.goalkeeper_df[self.goalkeeper_df['player_id'] == player_id]
        if target_stats.empty:
            return pd.DataFrame()
        
        features = ['saves', 'goals_conceded', 'big_saves']
        target_features = target_stats[features].iloc[0].values
        
        # Get other goalkeepers
        other_keepers = self.goalkeeper_df[self.goalkeeper_df['player_id'] != player_id]
        
        if other_keepers.empty:
            return pd.DataFrame()
        
        # Calculate distances
        distances = []
        for _, row in other_keepers.iterrows():
            dist = np.sqrt(sum((row[f] - target_features[i])**2 for i, f in enumerate(features)))
            distances.append(dist)
        
        other_keepers['distance'] = distances
        other_keepers = other_keepers.sort_values('distance')
        
        # Merge with player info
        result = pd.merge(
            other_keepers.head(top_n),
            self.players_df[['player_id', 'name', 'current_club']],
            on='player_id'
        )
        
        return result[['name', 'current_club', 'saves', 'goals_conceded', 'distance']]
    
    def get_league_statistics(self) -> pd.DataFrame:
        """Get aggregated statistics by league"""
        query = """
        SELECT 
            p.league_name,
            COUNT(DISTINCT p.player_id) as total_players,
            AVG(p.age) as avg_age,
            AVG(s.goals) as avg_goals,
            AVG(s.assists) as avg_assists,
            AVG(s.tackles) as avg_tackles,
            AVG(s.interceptions) as avg_interceptions
        FROM players p
        JOIN outfield_stats s ON p.player_id = s.player_id
        WHERE s.season = (SELECT MAX(season) FROM outfield_stats)
        GROUP BY p.league_name
        ORDER BY total_players DESC
        """
        
        try:
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            logger.error(f"Error getting league statistics: {e}")
            return pd.DataFrame()