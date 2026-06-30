import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from src.database import get_connection

def recommend_players(manager_preferences: dict, top_n: int = 5):
    """
    manager_preferences = {
        'position': 'Midfielder',
        'min_age': 18,
        'max_age': 25,
        'weights': {
            'interceptions': 0.4,
            'avg_km_per_match': 0.4,
            'assists': 0.2
        }
    }
    """
    conn = get_connection()
    
    # 1. Fetch relevant historical window data
    query = """
        SELECT p.*, s.interceptions, s.avg_km_per_match, s.assists, s.goals
        FROM players p
        JOIN outfield_stats s ON p.player_id = s.player_id
        WHERE p.position = :position 
          AND p.age BETWEEN :min_age AND :max_age
    """
    
    df = pd.read_sql_query(query, conn, params={
        'position': manager_preferences['position'],
        'min_age': manager_preferences['min_age'],
        'max_age': manager_preferences['max_age']
    })
    conn.close()
    
    if df.empty:
        return "No matching players found within filters."
        
    # 2. Extract targets and apply metric weight scaling
    features = list(manager_preferences['weights'].keys())
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[features])
    
    scaled_df = pd.DataFrame(scaled_features, columns=features)
    for col, weight in manager_preferences['weights'].items():
        scaled_df[col] = scaled_df[col] * weight
        
    # 3. Form a synthetic profile based on the optimized target matrix
    ideal_profile = scaled_df.max().values.reshape(1, -1)
    
    # 4. Measure proximity
    df['similarity_score'] = cosine_similarity(scaled_df, ideal_profile).flatten()
    
    return df.sort_values(by='similarity_score', ascending=False).head(top_n)