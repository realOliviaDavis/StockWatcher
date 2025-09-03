import requests
import json
import time
from datetime import datetime, timedelta

class StockAPI:
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        self.cache = {}
        self.cache_ttl = 60  # Cache for 60 seconds
    
    def get_stock_price(self, symbol):
        # Check cache first
        cache_key = symbol.upper()
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            url = f"{self.base_url}{symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                current_price = result['meta']['regularMarketPrice']
                
                stock_data = {
                    'symbol': symbol.upper(),
                    'price': current_price,
                    'currency': result['meta']['currency'],
                    'market_state': result['meta'].get('marketState', 'UNKNOWN'),
                    'previous_close': result['meta'].get('previousClose'),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Cache the result
                self.cache[cache_key] = (stock_data, time.time())
                return stock_data
            else:
                print(f"API returned status {response.status_code} for {symbol}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"Timeout fetching stock data for {symbol}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Connection error fetching stock data for {symbol}")
            return None
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols):
        results = {}
        for symbol in symbols:
            data = self.get_stock_price(symbol)
            if data:
                results[symbol.upper()] = data
            time.sleep(0.1)  # Rate limiting
        return results
    
    def validate_symbol(self, symbol):
        data = self.get_stock_price(symbol)
        return data is not None