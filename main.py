#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
from app.stock_api import StockAPI
from app.database import Database
from app.alerts import AlertSystem
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
stock_api = StockAPI()
db = Database()
alert_system = AlertSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    data = stock_api.get_stock_price(symbol)
    if data:
        db.save_stock_price(data['symbol'], data['price'], data['currency'])
        return jsonify(data)
    return jsonify({'error': 'Stock not found'}), 404

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
    alerts = alert_system.check_price_alerts(db, stock_api)
    return jsonify({
        'alerts_count': len(alerts),
        'alerts': alerts
    })

if __name__ == '__main__':
    app.run(debug=True)