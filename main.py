import sys
from src.database import initialize_database
from src.extract import fetch_league_data # Placeholder function for ingestion
from src.transform import clean_player_data

def run_pipeline():
    print("Starting Football Scouting Data Pipeline...")
    
    # Step 1: Initialize DB
    initialize_database()
    
    # Target Leagues Context
    leagues = [
        "Brazil Serie A", "Brazil Serie B", "Brazil Serie C",
        "Argentina Primera", "MLS", "Premier League", "Championship", 
        "La Liga", "Serie A IT", "Ligue 1", "Bundesliga", "Eredivisie", 
        "Liga Portugal", "Pro League BE", "Allsvenskan", "Russian Premier", 
        "Ukrainian Premier", "J1 League", "Saudi Pro League"
    ]
    
    print(f"Configured targeting for {len(leagues)} worldwide leagues.")
    
    # Step 2 & 3: Extract & Transform Loop (Conceptual placeholder)
    # raw_data = fetch_league_data(leagues)
    # cleaned_df = clean_player_data(raw_data)
    
    print("Pipeline executed successfully.")

if __name__ == "__main__":
    run_pipeline()