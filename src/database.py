import sqlite3
import os
from dotenv import load_load

load_dotenv()

def get_connection():
    db_path = os.getenv("DB_PATH", "data/scouting_database.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Read schema file
    schema_path = "sql/create_tables.sql"
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            cursor.executescript(f.read())
        conn.commit()
        print("Database tables initialized successfully.")
    else:
        print(f"Error: Schema file not found at {schema_path}")
    conn.close()