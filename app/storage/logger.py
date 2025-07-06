# app/storage/logger.py

import sqlite3
from datetime import datetime
import os

# Ensure DB folder
os.makedirs("db", exist_ok=True)
DB_PATH = "db/prompt_logs.db"

# Create table on first run
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS prompt_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                intent TEXT,
                original_prompt TEXT,
                optimized_prompt TEXT,
                original_response TEXT,
                optimized_response TEXT,
                feedback TEXT
            )
        ''')
        conn.commit()

# Insert a new prompt interaction
def log_prompt_interaction(intent, original_prompt, optimized_prompt, original_response=None, optimized_response=None, feedback=None):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO prompt_logs (timestamp, intent, original_prompt, optimized_prompt, original_response, optimized_response, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            intent,
            original_prompt,
            optimized_prompt,
            original_response,
            optimized_response,
            feedback
        ))
        conn.commit()

# Update feedback for a specific prompt log
def update_feedback(prompt_id: int, feedback: str):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            UPDATE prompt_logs
            SET feedback = ?
            WHERE id = ?
        ''', (feedback, prompt_id))
        conn.commit()

# Call on startup
init_db()
