#!/usr/bin/env python3

import sys
import os
import shutil
import sqlite3
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Database

def backup_database(backup_dir='backups'):
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'stock_data_backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        if os.path.exists('stock_data.db'):
            shutil.copy2('stock_data.db', backup_path)
            print(f"Database backed up to: {backup_path}")
            return backup_path
        else:
            print("No database file found to backup")
            return None
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

def export_data_to_json(backup_dir='backups'):
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_filename = f'stock_data_export_{timestamp}.json'
    export_path = os.path.join(backup_dir, export_filename)
    
    try:
        db = Database()
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        export_data = {}
        
        # Export watchlist
        cursor.execute('SELECT * FROM watchlist')
        watchlist_data = [dict(row) for row in cursor.fetchall()]
        export_data['watchlist'] = watchlist_data
        
        # Export recent stock prices (last 1000 records)
        cursor.execute('SELECT * FROM stock_prices ORDER BY timestamp DESC LIMIT 1000')
        prices_data = [dict(row) for row in cursor.fetchall()]
        export_data['stock_prices'] = prices_data
        
        # Export portfolio if exists
        try:
            cursor.execute('SELECT * FROM portfolio')
            portfolio_data = [dict(row) for row in cursor.fetchall()]
            export_data['portfolio'] = portfolio_data
        except:
            export_data['portfolio'] = []
        
        # Export transactions if exists  
        try:
            cursor.execute('SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT 500')
            transactions_data = [dict(row) for row in cursor.fetchall()]
            export_data['transactions'] = transactions_data
        except:
            export_data['transactions'] = []
        
        conn.close()
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Data exported to JSON: {export_path}")
        return export_path
        
    except Exception as e:
        print(f"Export failed: {e}")
        return None

def cleanup_old_backups(backup_dir='backups', keep_count=5):
    if not os.path.exists(backup_dir):
        return
    
    # Get all backup files
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.startswith('stock_data_backup_') and filename.endswith('.db'):
            filepath = os.path.join(backup_dir, filename)
            backup_files.append((filepath, os.path.getmtime(filepath)))
    
    # Sort by modification time (newest first)
    backup_files.sort(key=lambda x: x[1], reverse=True)
    
    # Remove old backups
    if len(backup_files) > keep_count:
        for filepath, _ in backup_files[keep_count:]:
            try:
                os.remove(filepath)
                print(f"Removed old backup: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"Failed to remove {filepath}: {e}")

def main():
    print("StockWatcher Data Backup Tool")
    print("=" * 40)
    
    # Create database backup
    backup_path = backup_database()
    
    # Export data to JSON
    json_path = export_data_to_json()
    
    # Cleanup old backups
    cleanup_old_backups()
    
    print("\nBackup completed!")

if __name__ == "__main__":
    main()