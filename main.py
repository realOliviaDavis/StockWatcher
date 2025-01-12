#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
from app.stock_api import StockAPI
from app.database import Database

app = Flask(__name__)
stock_api = StockAPI()
db = Database()

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

if __name__ == '__main__':
    app.run(debug=True)