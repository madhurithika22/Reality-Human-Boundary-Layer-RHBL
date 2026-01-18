import sqlite3
import json
import datetime
import os

DB_NAME = "rhbl_logs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # NEW STRUCTURE: Matches your requested JSON format perfectly
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            layer TEXT DEFAULT 'human',
            score REAL,
            confidence_interval TEXT,
            quality REAL,
            violated_rules TEXT,
            full_json TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"📂 Database initialized: {DB_NAME}")

def save_log(stats_dict):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Extract Data
        layer = stats_dict.get("layer", "human")
        score = float(stats_dict.get("score", 0.0))
        quality = float(stats_dict.get("quality", 0.0))
        
        # 2. Convert Arrays to Strings for SQLite
        # Example: [0.8, 1.0] -> "[0.8, 1.0]"
        conf_interval_str = json.dumps(stats_dict.get("confidence_interval", [0.0, 1.0]))
        
        # Example: ["Did Not Smile"] -> "['Did Not Smile']"
        violated_rules_str = json.dumps(stats_dict.get("violated_rules", []))
        
        # 3. Create the Full JSON Dump (for backup/API usage)
        full_json_obj = {
            "layer": layer,
            "score": score,
            "confidence_interval": stats_dict.get("confidence_interval", [0.0, 1.0]),
            "quality": quality,
            "violated_rules": stats_dict.get("violated_rules", [])
        }
        full_json_str = json.dumps(full_json_obj)
        
        # 4. Insert into the new columns
        cursor.execute(
            """INSERT INTO logs 
               (timestamp, layer, score, confidence_interval, quality, violated_rules, full_json) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""", 
            (timestamp, layer, score, conf_interval_str, quality, violated_rules_str, full_json_str)
        )
        
        conn.commit()
        conn.close()
        
        # Confirmation Print
        print(f"💾 DB WRITE: Score={score} | Rules={violated_rules_str}")
        
    except Exception as e:
        print(f"❌ DB ERROR: {e}")

# Run initialization immediately
init_db()