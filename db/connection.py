# db/connection.py
import sqlite3
from config import DATABASE_PATH

def get_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This lets us access columns by name
    return conn

class DatabaseConnection:
    def __enter__(self):
        self.conn = get_connection()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()