import pandas as pd

def clean_player_data(raw_data: list) -> pd.DataFrame:
    """
    Cleans demographic information and applies default constraints.
    """
    df = pd.DataFrame(raw_data)
    if df.empty:
        return df
        
    # Standardize data structures
    df['height_cm'] = pd.to_numeric(df['height_cm'], errors='coerce').fillna(180).astype(int)
    df['weight_kg'] = pd.to_numeric(df['weight_kg'], errors='coerce').fillna(75).astype(int)
    df['age'] = pd.to_numeric(df['age'], errors='coerce').astype(int)
    df['preferred_foot'] = df['preferred_foot'].apply(lambda x: x if x in ['Left', 'Right'] else 'Right')
    
    return df