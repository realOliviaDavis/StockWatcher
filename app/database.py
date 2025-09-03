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
    
    def add_to_watchlist(self, symbol, target_price=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO watchlist (symbol, target_price) VALUES (?, ?)',
                (symbol, target_price)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Symbol already exists
            return False
        finally:
            conn.close()
    
    def get_watchlist(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT symbol, target_price, alert_enabled FROM watchlist ORDER BY created_at DESC')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def remove_from_watchlist(self, symbol):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM watchlist WHERE symbol = ?', (symbol,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def update_alert_status(self, symbol, enabled):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE watchlist SET alert_enabled = ? WHERE symbol = ?',
            (enabled, symbol)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0