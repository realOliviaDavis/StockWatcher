import sqlite3
from datetime import datetime

class Portfolio:
    def __init__(self, db_path='stock_data.db'):
        self.db_path = db_path
        self.init_portfolio_tables()
    
    def init_portfolio_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                shares REAL NOT NULL,
                purchase_price REAL NOT NULL,
                purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                shares REAL NOT NULL,
                price REAL NOT NULL,
                transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_value REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_position(self, symbol, shares, purchase_price, notes=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO portfolio (symbol, shares, purchase_price, notes) VALUES (?, ?, ?, ?)',
            (symbol, shares, purchase_price, notes)
        )
        
        # Record transaction
        total_value = shares * purchase_price
        cursor.execute(
            'INSERT INTO transactions (symbol, transaction_type, shares, price, total_value) VALUES (?, ?, ?, ?, ?)',
            (symbol, 'BUY', shares, purchase_price, total_value)
        )
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_portfolio_summary(self, stock_api):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, SUM(shares) as total_shares, AVG(purchase_price) as avg_price 
            FROM portfolio 
            GROUP BY symbol 
            HAVING total_shares > 0
        ''')
        
        positions = cursor.fetchall()
        conn.close()
        
        portfolio_data = []
        total_invested = 0
        total_current_value = 0
        
        for symbol, shares, avg_price in positions:
            current_data = stock_api.get_stock_price(symbol)
            current_price = current_data['price'] if current_data else avg_price
            
            position_value = shares * current_price
            invested_value = shares * avg_price
            profit_loss = position_value - invested_value
            profit_loss_pct = (profit_loss / invested_value) * 100 if invested_value > 0 else 0
            
            portfolio_data.append({
                'symbol': symbol,
                'shares': shares,
                'avg_price': avg_price,
                'current_price': current_price,
                'position_value': position_value,
                'invested_value': invested_value,
                'profit_loss': profit_loss,
                'profit_loss_pct': profit_loss_pct
            })
            
            total_invested += invested_value
            total_current_value += position_value
        
        total_profit_loss = total_current_value - total_invested
        total_profit_loss_pct = (total_profit_loss / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            'positions': portfolio_data,
            'summary': {
                'total_invested': total_invested,
                'total_current_value': total_current_value,
                'total_profit_loss': total_profit_loss,
                'total_profit_loss_pct': total_profit_loss_pct
            }
        }
    
    def get_transaction_history(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT 50'
        )
        
        transactions = cursor.fetchall()
        conn.close()
        return transactions