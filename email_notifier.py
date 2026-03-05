import smtplib
import asyncio
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import EMAIL_CONFIG

class EmailNotifier:
    """Handles email notifications for the arbitrage bot"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.smtp_server = EMAIL_CONFIG['smtp_server']
        self.smtp_port = EMAIL_CONFIG['smtp_port']
        self.email = EMAIL_CONFIG['email']
        self.password = EMAIL_CONFIG['password']
        self.recipient = EMAIL_CONFIG['recipient']
    
    async def send_notification(self, subject: str, message: str):
        """Send email notification asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email, subject, message)
            self.logger.info(f"Email notification sent: {subject}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
    
    def _send_email(self, subject: str, message: str):
        """Send email synchronously"""
        if not all([self.email, self.password, self.recipient]):
            self.logger.warning("Email configuration incomplete, skipping notification")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = self.recipient
            msg['Subject'] = f"[Crypto Arbitrage Bot] {subject}"
            
            # Add timestamp to message
            timestamped_message = f"""
{message}

---
Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Crypto Arbitrage Bot v1.0
            """
            
            msg.attach(MIMEText(timestamped_message, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.email, self.recipient, text)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"SMTP error: {str(e)}")
            raise
    
    async def send_daily_summary(self, trades: list, total_profit: float, total_volume: float):
        """Send daily trading summary"""
        subject = f"Daily Trading Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        if not trades:
            message = """
Daily Trading Summary:

No trades executed today.

Total Volume: $0.00
Total Profit: $0.00
            """
        else:
            successful_trades = [t for t in trades if t['status'] == 'SUCCESS']
            failed_trades = [t for t in trades if t['status'] in ['FAILED', 'ERROR']]
            
            message = f"""
Daily Trading Summary:

Total Trades: {len(trades)}
Successful: {len(successful_trades)}
Failed: {len(failed_trades)}

Total Volume: ${total_volume:.2f}
Total Profit: ${total_profit:.2f}
Success Rate: {len(successful_trades)/len(trades)*100:.1f}%

Recent Trades:
"""
            
            for trade in trades[-5:]:  # Last 5 trades
                status_emoji = "✅" if trade['status'] == 'SUCCESS' else "❌"
                message += f"""
{status_emoji} {trade['symbol']} - {trade['buy_exchange']} → {trade['sell_exchange']}
   Profit: ${trade['profit']:.2f} ({trade['profit_percentage']:.2%})
   Time: {trade['timestamp'][:19]}
"""
        
        await self.send_notification(subject, message)
    
    async def send_error_alert(self, error_message: str, context: str = ""):
        """Send error alert notification"""
        subject = "🚨 Bot Error Alert"
        
        message = f"""
An error occurred in the Crypto Arbitrage Bot:

Error: {error_message}
Context: {context}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Please check the bot logs for more details.
        """
        
        await self.send_notification(subject, message)
    
    async def send_startup_notification(self):
        """Send notification when bot starts"""
        subject = "🚀 Bot Started"
        
        message = """
Crypto Arbitrage Bot has started successfully.

The bot is now monitoring the following exchanges:
- Binance
- Coinbase
- Kraken  
- KuCoin

Tracking cryptocurrencies:
- BTC/USDT
- ETH/USDT
- BNB/USDT
- ADA/USDT
- SOL/USDT
- DOT/USDT

Risk Management Settings:
- Minimum profit threshold: 1.5%
- Maximum trade amount: $1,000
- Daily trading limit: $5,000
- Stop loss: 0.5%

The bot will send notifications for all executed trades and daily summaries.
        """
        
        await self.send_notification(subject, message)
    
    async def send_shutdown_notification(self):
        """Send notification when bot shuts down"""
        subject = "🛑 Bot Stopped"
        
        message = """
Crypto Arbitrage Bot has been stopped.

All trading activities have ceased. The bot will need to be manually restarted to resume operations.
        """
        
        await self.send_notification(subject, message)