#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
from app.stock_api import StockAPI

app = Flask(__name__)
stock_api = StockAPI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    data = stock_api.get_stock_price(symbol)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Stock not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)