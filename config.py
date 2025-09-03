import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-stockwatcher-2025'
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'stock_data.db'
    STOCK_API_TIMEOUT = 10
    PRICE_UPDATE_INTERVAL = 300  # 5 minutes
    MAX_HISTORY_RECORDS = 1000
    
    # Alert settings
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_USER = os.environ.get('EMAIL_USER')
    EMAIL_PASS = os.environ.get('EMAIL_PASS')
    
    # Default watchlist symbols
    DEFAULT_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']