#!/usr/bin/env python3

import sys
import os
import time
import schedule
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.stock_api import StockAPI
from app.database import Database
from app.alerts import AlertSystem

def check_and_send_alerts():
    print(f"[{datetime.now()}] Checking price alerts...")
    
    stock_api = StockAPI()
    db = Database()
    alert_system = AlertSystem()
    
    try:
        alerts = alert_system.check_price_alerts(db, stock_api)
        
        if alerts:
            print(f"Found {len(alerts)} alerts to process")
            
            for alert in alerts:
                print(f"Alert: {alert['symbol']} at ${alert['current_price']:.2f}")
                alert_system.send_email_alert(alert)
        else:
            print("No alerts triggered")
            
    except Exception as e:
        print(f"Error checking alerts: {e}")

def main():
    print("Starting StockWatcher Alert Monitor...")
    print("Checking for alerts every 5 minutes")
    
    # Schedule alert checks every 5 minutes
    schedule.every(5).minutes.do(check_and_send_alerts)
    
    # Run initial check
    check_and_send_alerts()
    
    # Keep the script running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nAlert monitor stopped")

if __name__ == "__main__":
    main()