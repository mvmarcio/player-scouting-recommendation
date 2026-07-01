"""
Data extraction module for football player statistics
"""
import requests
import json
import time
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import random
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class FootballDataExtractor:
    """
    Extract football player data from various sources
    """
    
    # Position mapping
    POSITION_MAPPING = {
        'GK': 'Goalkeeper',
        'CB': 'Defender',
        'LB': 'Defender',
        'RB': 'Defender',
        'LWB': 'Defender',
        'RWB': 'Defender',
        'CDM': 'Midfielder',
        'CM': 'Midfielder',
        'CAM': 'Midfielder',
        'LM': 'Midfielder',
        'RM': 'Midfielder',
        'LW': 'Forward',
        'RW': 'Forward',
        'ST': 'Forward',
        'CF': 'Forward'
    }
    
    def __init__(self, api_key: Optional[str] = None):
        # Get API key from .env if not provided
        self.api_key = api_key or os.getenv('FOOTBALL_API_KEY')
        self.base_url = os.getenv('API_BASE_URL', 'https://v3.football.api-sports.io')
        self.session = requests.Session()
        
        if self.api_key and self.api_key != 'your_api_key_here':
            self.session.headers.update({
                'x-rapidapi-key': self.api_key,
                'x-rapidapi-host': 'v3.football.api-sports.io'
            })
            logger.info("API key loaded from .env")
        else:
            logger.info("No valid API key found, using mock data")
        
    def fetch_player_stats(self, league_id: int, season: int) -> Dict:
        """
        Fetch player statistics for a specific league and season
        
        Args:
            league_id: League ID (71 = Brazilian Serie A)
            season: Season year (e.g., 2026)
        
        Returns:
            Dictionary with players and their stats
        """
        logger.info(f"Extracting data from league {league_id} - season {season}")
        
        if self.api_key and self.api_key != 'your_api_key_here':
            # Real API call
            return self._fetch_from_api(league_id, season)
        else:
            # Mock data for testing
            logger.info("Using mock data for testing")
            return self._generate_mock_data(league_id, season)
    
    def _fetch_from_api(self, league_id: int, season: int) -> Dict:
        """Fetch data from Football API"""
        try:
            # Get players
            response = self.session.get(
                f"{self.base_url}/players",
                params={
                    'league': league_id,
                    'season': season
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Process API response
            players_data = []
            for player_data in data.get('response', []):
                processed = self._process_api_response(player_data, league_id, season)
                if processed:
                    players_data.append(processed)
            
            logger.info(f"Extracted {len(players_data)} players from API")
            return {'players': players_data, 'season': f"{season-1}/{season}"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {'players': [], 'season': f"{season-1}/{season}"}
    
    def _process_api_response(self, player_data: Dict, league_id: int, season: int) -> Dict:
        """Process API response into standardized format"""
        try:
            player_info = player_data.get('player', {})
            statistics = player_data.get('statistics', [{}])[0]
            
            position = statistics.get('position', 'Unknown')
            position_category = self.POSITION_MAPPING.get(position, 'Unknown')
            is_goalkeeper = position_category == 'Goalkeeper'
            
            return {
                'player_id': str(player_info.get('id', '')),
                'name': player_info.get('name', 'Unknown'),
                'nationality': player_info.get('nationality', 'Unknown'),
                'age': player_info.get('age'),
                'height_cm': self._parse_height_cm(player_info.get('height')),
                'weight_kg': self._parse_weight_kg(player_info.get('weight')),
                'preferred_foot': player_info.get('foot', 'Right'),
                'injury_history': '[]',
                'current_club': statistics.get('team', {}).get('name', 'Unknown'),
                'league_name': self._get_league_name(league_id),
                'position': position_category,
                'season': f"{season-1}/{season}",
                'matches_played': statistics.get('games', {}).get('appearences', 0),
                'goals': statistics.get('goals', {}).get('total', 0),
                'assists': statistics.get('goals', {}).get('assists', 0),
                'goal_contributions': statistics.get('goals', {}).get('total', 0) + statistics.get('goals', {}).get('assists', 0),
                'shots': statistics.get('shots', {}).get('total', 0),
                'tackles': statistics.get('tackles', {}).get('total', 0),
                'interceptions': statistics.get('interceptions', {}).get('total', 0),
                'yellow_cards': statistics.get('cards', {}).get('yellow', 0),
                'red_cards': statistics.get('cards', {}).get('red', 0),
                # Goalkeeper specific
                'goals_conceded': statistics.get('goals', {}).get('conceded', 0) if is_goalkeeper else 0,
                'saves': statistics.get('goals', {}).get('saves', 0) if is_goalkeeper else 0,
                'big_saves': 0,
                'is_goalkeeper': is_goalkeeper
            }
        except Exception as e:
            logger.error(f"Error processing player data: {e}")
            return None
    
    def _parse_height_cm(self, height_str: str) -> int:
        """Parse height from string to cm"""
        if not height_str:
            return None
        try:
            if 'cm' in height_str:
                return int(height_str.replace('cm', '').strip())
            return int(height_str)
        except:
            return None
    
    def _parse_weight_kg(self, weight_str: str) -> int:
        """Parse weight from string to kg"""
        if not weight_str:
            return None
        try:
            if 'kg' in weight_str:
                return int(weight_str.replace('kg', '').strip())
            return int(weight_str)
        except:
            return None
    
    def _get_league_name(self, league_id: int) -> str:
        """Get league name from ID"""
        league_names = {
            71: 'Brasileirão Série A',
            72: 'Brasileirão Série B',
            73: 'Brasileirão Série C',
            128: 'Argentina Liga Profesional',
            129: 'Chile Primera Division',
            130: 'Colombia Primera A',
            131: 'Uruguay Primera Division',
            132: 'Paraguay Division Profesional',
            133: 'Ecuador Liga Pro',
            134: 'Peru Liga 1',
            135: 'Bolivia Division Profesional',
            136: 'Venezuela Primera Division',
            137: 'Mexico Liga MX',
            138: 'MLS',
            39: 'Premier League',
            40: 'Championship',
            140: 'La Liga',
            135: 'Serie A Italy',
            61: 'Ligue 1',
            78: 'Bundesliga',
            88: 'Eredivisie',
            94: 'Primeira Liga',
            144: 'Belgium Pro League',
            48: 'Sweden Allsvenskan',
            66: 'Russia Premier League',
            68: 'Ukraine Premier League',
            98: 'Japan J-League',
            307: 'Saudi Pro League'
        }
        return league_names.get(league_id, f'League {league_id}')
    
    def _generate_mock_data(self, league_id: int, season: int) -> Dict:
        """Generate mock data for testing"""
        league_name = self._get_league_name(league_id)
        positions = ['GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST']
        nationalities = ['BRA', 'ARG', 'URU', 'COL', 'ECU', 'PAR', 'PER', 'CHI', 'ENG', 'ESP', 'ITA', 'GER']
        
        players_data = []
        num_players = random.randint(20, 30)
        
        for i in range(num_players):
            position = random.choice(positions)
            position_category = self.POSITION_MAPPING.get(position, 'Unknown')
            is_goalkeeper = position_category == 'Goalkeeper'
            
            player = {
                'player_id': str(10000 + i),
                'name': f'Player_{i+1}',
                'nationality': random.choice(nationalities),
                'age': random.randint(18, 35),
                'height_cm': random.randint(165, 195),
                'weight_kg': random.randint(60, 90),
                'preferred_foot': random.choice(['Left', 'Right']),
                'injury_history': json.dumps(
                    ['2024-03-15', '2024-08-20'] if random.random() > 0.7 else []
                ),
                'current_club': f'Team_{random.randint(1, 10)}',
                'league_name': league_name,
                'position': position_category,
                'season': f"{season-1}/{season}",
                'matches_played': random.randint(10, 38),
                'goals': random.randint(0, 15),
                'assists': random.randint(0, 10),
                'goal_contributions': random.randint(0, 20),
                'shots': random.randint(10, 60),
                'tackles': random.randint(10, 50),
                'interceptions': random.randint(5, 30),
                'aerial_duels_won_def': random.randint(10, 40),
                'aerial_duels_won_off': random.randint(5, 25),
                'avg_km_per_match': round(random.uniform(8, 12), 1),
                'yellow_cards': random.randint(0, 8),
                'red_cards': random.randint(0, 2),
                'goals_conceded': random.randint(0, 25) if is_goalkeeper else 0,
                'saves': random.randint(0, 80) if is_goalkeeper else 0,
                'big_saves': random.randint(0, 20) if is_goalkeeper else 0,
                'is_goalkeeper': is_goalkeeper
            }
            players_data.append(player)
        
        return {'players': players_data, 'season': f"{season-1}/{season}"}
    
    def fetch_multiple_leagues(self, leagues: List[int], seasons: List[int]) -> Dict:
        """Fetch data from multiple leagues and seasons"""
        all_players = []
        
        for league in leagues:
            for season in seasons:
                data = self.fetch_player_stats(league, season)
                all_players.extend(data.get('players', []))
                time.sleep(0.5)  # Be nice to API
        
        return {'players': all_players}