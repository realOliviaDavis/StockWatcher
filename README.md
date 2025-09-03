# StockWatcher

A comprehensive stock price monitoring and portfolio tracking tool.

## Features

### 📈 Stock Monitoring
- Real-time stock price fetching via Yahoo Finance API
- Price history tracking and visualization
- Caching system for improved performance
- Market state indicators

### 📋 Watchlist Management
- Add/remove stocks from personal watchlist
- Set target price alerts
- Quick price checking for watchlisted stocks
- Toggle alert notifications

### 💼 Portfolio Tracking
- Track stock positions and performance
- Calculate profit/loss and percentage returns
- Transaction history logging
- Portfolio value summaries

### 🔔 Alert System
- Email alerts for price targets (configurable)
- Automated monitoring script
- Custom threshold settings

### 🔍 Stock Comparison
- Compare multiple stocks side-by-side
- Real-time price comparison
- Market state comparison

### 🛠 Additional Tools
- Database backup and export utilities
- Data cleanup and optimization
- Automated alert monitoring script

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Configuration

Create environment variables for email alerts:
- `EMAIL_USER`: Your email address
- `EMAIL_PASS`: Your email password/app password
- `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)

## Scripts

### Alert Monitor
Run continuous price alert monitoring:
```bash
python scripts/monitor_alerts.py
```

### Data Backup
Backup database and export data:
```bash
python scripts/backup_data.py
```

## API Endpoints

- `GET /api/stock/<symbol>` - Get current stock price
- `GET /api/history/<symbol>` - Get price history
- `GET/POST /api/watchlist` - Manage watchlist
- `DELETE /api/watchlist/<symbol>` - Remove from watchlist
- `GET/POST /api/portfolio` - Manage portfolio
- `GET /api/compare?symbols=AAPL,GOOGL` - Compare stocks
- `GET /api/alerts/check` - Check price alerts

## Database

Uses SQLite for data storage with tables:
- `stock_prices` - Historical price data
- `watchlist` - User watchlist with alerts
- `portfolio` - User stock positions
- `transactions` - Trading history

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **APIs**: Yahoo Finance
- **Styling**: Custom CSS with responsive design