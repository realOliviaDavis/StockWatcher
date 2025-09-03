import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config

class AlertSystem:
    def __init__(self):
        self.config = Config()
    
    def check_price_alerts(self, db, stock_api):
        alerts_triggered = []
        watchlist = db.get_watchlist()
        
        for item in watchlist:
            symbol, target_price, alert_enabled = item
            if not alert_enabled:
                continue
                
            current_data = stock_api.get_stock_price(symbol)
            if current_data:
                current_price = current_data['price']
                
                # Simple alert logic - trigger if price crosses target
                if self._should_trigger_alert(current_price, target_price):
                    alert_info = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'target_price': target_price,
                        'timestamp': datetime.now()
                    }
                    alerts_triggered.append(alert_info)
                    
        return alerts_triggered
    
    def _should_trigger_alert(self, current_price, target_price):
        # Simple threshold check
        return abs(current_price - target_price) / target_price < 0.02  # 2% threshold
    
    def send_email_alert(self, alert_info):
        if not self.config.EMAIL_USER or not self.config.EMAIL_PASS:
            print(f"Email not configured, alert: {alert_info['symbol']} hit target")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.EMAIL_USER
            msg['To'] = self.config.EMAIL_USER  # Send to self for now
            msg['Subject'] = f"StockWatcher Alert: {alert_info['symbol']}"
            
            body = f"""
            Stock Alert Triggered!
            
            Symbol: {alert_info['symbol']}
            Current Price: ${alert_info['current_price']:.2f}
            Target Price: ${alert_info['target_price']:.2f}
            Time: {alert_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.EMAIL_USER, self.config.EMAIL_PASS)
            server.send_message(msg)
            server.quit()
            return True
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False