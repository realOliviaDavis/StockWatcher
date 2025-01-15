import requests
import json

class StockAPI:
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
    
    def get_stock_price(self, symbol):
        try:
            url = f"{self.base_url}{symbol}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                current_price = result['meta']['regularMarketPrice']
                return {
                    'symbol': symbol.upper(),
                    'price': current_price,
                    'currency': result['meta']['currency']
                }
            return None
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return None