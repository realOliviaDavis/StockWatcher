import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='stock_data.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                target_price REAL,
                alert_enabled BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_stock_price(self, symbol, price, currency):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO stock_prices (symbol, price, currency) VALUES (?, ?, ?)',
            (symbol, price, currency)
        )
        
        conn.commit()
        conn.close()
    
    def get_stock_history(self, symbol, limit=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT price, timestamp FROM stock_prices WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?',
            (symbol, limit)
        )
        
        results = cursor.fetchall()
        conn.close()
        return results