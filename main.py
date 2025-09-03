#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
from app.stock_api import StockAPI
from app.database import Database
from app.alerts import AlertSystem
from app.portfolio import Portfolio
from config import Config
import traceback

app = Flask(__name__)
app.config.from_object(Config)
stock_api = StockAPI()
db = Database()
alert_system = AlertSystem()
portfolio = Portfolio()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    try:
        if not stock_api.validate_symbol(symbol):
            return jsonify({'error': 'Invalid stock symbol'}), 400
            
        data = stock_api.get_stock_price(symbol)
        if data:
            db.save_stock_price(data['symbol'], data['price'], data['currency'])
            return jsonify(data)
        return jsonify({'error': 'Stock data unavailable'}), 404
    except Exception as e:
        app.logger.error(f"Error in get_stock: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/history/<symbol>')
def get_stock_history(symbol):
    history = db.get_stock_history(symbol.upper())
    if history:
        return jsonify({
            'symbol': symbol.upper(),
            'history': [{'price': price, 'timestamp': timestamp} for price, timestamp in history]
        })
    return jsonify({'error': 'No history found'}), 404

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    watchlist = db.get_watchlist()
    return jsonify([{
        'symbol': symbol,
        'target_price': target_price,
        'alert_enabled': bool(alert_enabled)
    } for symbol, target_price, alert_enabled in watchlist])

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    target_price = data.get('target_price')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    if db.add_to_watchlist(symbol, target_price):
        return jsonify({'message': f'{symbol} added to watchlist'})
    else:
        return jsonify({'error': 'Symbol already in watchlist'}), 400

@app.route('/api/watchlist/<symbol>', methods=['DELETE'])
def remove_from_watchlist(symbol):
    if db.remove_from_watchlist(symbol.upper()):
        return jsonify({'message': f'{symbol.upper()} removed from watchlist'})
    else:
        return jsonify({'error': 'Symbol not found in watchlist'}), 404

@app.route('/api/alerts/check')
def check_alerts():
    try:
        alerts = alert_system.check_price_alerts(db, stock_api)
        return jsonify({
            'alerts_count': len(alerts),
            'alerts': alerts
        })
    except Exception as e:
        app.logger.error(f"Error checking alerts: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to check alerts'}), 500

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    try:
        portfolio_data = portfolio.get_portfolio_summary(stock_api)
        return jsonify(portfolio_data)
    except Exception as e:
        app.logger.error(f"Error getting portfolio: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to get portfolio data'}), 500

@app.route('/api/portfolio', methods=['POST'])
def add_portfolio_position():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        shares = data.get('shares')
        price = data.get('price')
        notes = data.get('notes', '')
        
        if not symbol or not shares or not price:
            return jsonify({'error': 'Symbol, shares, and price are required'}), 400
        
        if not stock_api.validate_symbol(symbol):
            return jsonify({'error': 'Invalid stock symbol'}), 400
            
        position_id = portfolio.add_position(symbol, float(shares), float(price), notes)
        return jsonify({
            'message': f'Added {shares} shares of {symbol}',
            'position_id': position_id
        })
    except ValueError:
        return jsonify({'error': 'Invalid number format'}), 400
    except Exception as e:
        app.logger.error(f"Error adding portfolio position: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to add position'}), 500

@app.route('/api/compare')
def compare_stocks():
    try:
        symbols = request.args.get('symbols', '').split(',')
        symbols = [s.strip().upper() for s in symbols if s.strip()]
        
        if len(symbols) < 2:
            return jsonify({'error': 'At least 2 symbols required'}), 400
        
        comparison_data = stock_api.get_multiple_prices(symbols)
        return jsonify(comparison_data)
    except Exception as e:
        app.logger.error(f"Error comparing stocks: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to compare stocks'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)