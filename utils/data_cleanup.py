import sqlite3
import os
from datetime import datetime, timedelta

class DataCleanup:
    def __init__(self, db_path='stock_data.db'):
        self.db_path = db_path
    
    def cleanup_old_data(self, days_to_keep=30):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean old stock prices
        cursor.execute(
            'DELETE FROM stock_prices WHERE timestamp < ?',
            (cutoff_date.isoformat(),)
        )
        
        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_deleted
    
    def optimize_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('VACUUM')
        cursor.execute('ANALYZE')
        
        conn.close()
    
    def get_database_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count records in each table
        cursor.execute('SELECT COUNT(*) FROM stock_prices')
        stats['stock_prices_count'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM watchlist')
        stats['watchlist_count'] = cursor.fetchone()[0]
        
        try:
            cursor.execute('SELECT COUNT(*) FROM portfolio')
            stats['portfolio_count'] = cursor.fetchone()[0]
        except:
            stats['portfolio_count'] = 0
        
        try:
            cursor.execute('SELECT COUNT(*) FROM transactions')
            stats['transactions_count'] = cursor.fetchone()[0]
        except:
            stats['transactions_count'] = 0
        
        # Get database file size
        if os.path.exists(self.db_path):
            stats['file_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
        else:
            stats['file_size_mb'] = 0
        
        conn.close()
        return stats