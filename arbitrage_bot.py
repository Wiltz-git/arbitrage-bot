import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List
import json
import sqlite3
from exchange_manager import ExchangeManager
from email_notifier import EmailNotifier
from config import TRADING_CONFIG, LOGGING_CONFIG, DATABASE_CONFIG

class ArbitrageBot:
    """Main arbitrage trading bot that monitors and executes trades"""
    
    def __init__(self):
        self.setup_logging()
        self.exchange_manager = ExchangeManager()
        self.email_notifier = EmailNotifier()
        self.setup_database()
        
        # Trading state
        self.is_running = False
        self.daily_volume = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.hourly_trades = []
        self.last_opportunities = []
        
        self.logger.info("Arbitrage Bot initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOGGING_CONFIG['file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup SQLite database for trade history"""
        conn = sqlite3.connect(DATABASE_CONFIG['file'])
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                buy_exchange TEXT,
                sell_exchange TEXT,
                buy_price REAL,
                sell_price REAL,
                amount REAL,
                profit REAL,
                profit_percentage REAL,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                buy_exchange TEXT,
                sell_exchange TEXT,
                buy_price REAL,
                sell_price REAL,
                profit_percentage REAL,
                executed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def start(self):
        """Start the arbitrage bot"""
        self.is_running = True
        self.logger.info("Starting Arbitrage Bot...")
        
        while self.is_running:
            try:
                await self.scan_and_trade()
                await asyncio.sleep(5)  # Scan every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                await asyncio.sleep(10)  # Wait longer on error
    
    def stop(self):
        """Stop the arbitrage bot"""
        self.is_running = False
        self.logger.info("Stopping Arbitrage Bot...")
    
    async def scan_and_trade(self):
        """Scan for opportunities and execute trades"""
        # Reset daily volume if needed
        self._check_daily_reset()
        
        # Check if we've hit daily limits
        if self.daily_volume >= TRADING_CONFIG['daily_limit']:
            self.logger.info("Daily trading limit reached")
            return
        
        # Check hourly trade limit
        if self._get_hourly_trade_count() >= TRADING_CONFIG['max_trades_per_hour']:
            self.logger.info("Hourly trade limit reached")
            return
        
        opportunities = []
        
        # Scan each cryptocurrency
        for symbol in TRADING_CONFIG['cryptocurrencies']:
            try:
                # Get prices from all exchanges
                prices = await self.exchange_manager.get_ticker_prices(symbol)
                
                if len(prices) < 2:
                    continue
                
                # Find arbitrage opportunities
                symbol_opportunities = self.exchange_manager.find_arbitrage_opportunities(prices)
                
                for opp in symbol_opportunities:
                    opp['symbol'] = symbol
                    opp['timestamp'] = datetime.now().isoformat()
                    opportunities.append(opp)
                
                # Log opportunities to database
                self._log_opportunities(symbol_opportunities, symbol)
                
            except Exception as e:
                self.logger.error(f"Error scanning {symbol}: {str(e)}")
        
        # Store current opportunities
        self.last_opportunities = opportunities
        
        # Execute the most profitable opportunity
        if opportunities:
            best_opportunity = opportunities[0]
            
            if await self._should_execute_trade(best_opportunity):
                await self._execute_trade(best_opportunity)
    
    async def _should_execute_trade(self, opportunity: Dict) -> bool:
        """Determine if a trade should be executed based on risk management"""
        # Check profit threshold
        if opportunity['profit_percentage'] < TRADING_CONFIG['min_profit_threshold']:
            return False
        
        # Check if we have enough balance
        if opportunity['recommended_amount'] < 10:  # Minimum $10 trade
            return False
        
        # Check daily volume limit
        if self.daily_volume + opportunity['recommended_amount'] > TRADING_CONFIG['daily_limit']:
            return False
        
        # Additional risk checks can be added here
        return True
    
    async def _execute_trade(self, opportunity: Dict):
        """Execute an arbitrage trade"""
        self.logger.info(f"Executing trade: {opportunity['symbol']} - "
                        f"{opportunity['profit_percentage']:.2%} profit")
        
        try:
            # Execute the trade
            result = await self.exchange_manager.execute_arbitrage_trade(
                opportunity, opportunity['symbol']
            )
            
            if result['success']:
                # Update trading state
                self.daily_volume += opportunity['recommended_amount']
                self.hourly_trades.append(datetime.now())
                
                # Log successful trade
                self._log_trade(opportunity, result, 'SUCCESS')
                
                # Send email notification
                await self._send_trade_notification(opportunity, result, True)
                
                self.logger.info(f"Trade executed successfully. Profit: ${result['profit']:.2f}")
                
            else:
                # Log failed trade
                self._log_trade(opportunity, result, 'FAILED')
                
                # Send failure notification
                await self._send_trade_notification(opportunity, result, False)
                
                self.logger.error(f"Trade execution failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")
            self._log_trade(opportunity, {'error': str(e)}, 'ERROR')
    
    def _check_daily_reset(self):
        """Check if we need to reset daily volume"""
        now = datetime.now()
        if now >= self.daily_reset_time + timedelta(days=1):
            self.daily_volume = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            self.logger.info("Daily trading volume reset")
    
    def _get_hourly_trade_count(self) -> int:
        """Get number of trades in the last hour"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Remove old trades
        self.hourly_trades = [t for t in self.hourly_trades if t > hour_ago]
        
        return len(self.hourly_trades)
    
    def _log_opportunities(self, opportunities: List[Dict], symbol: str):
        """Log opportunities to database"""
        conn = sqlite3.connect(DATABASE_CONFIG['file'])
        cursor = conn.cursor()
        
        for opp in opportunities:
            cursor.execute('''
                INSERT INTO opportunities 
                (timestamp, symbol, buy_exchange, sell_exchange, buy_price, sell_price, profit_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                symbol,
                opp['buy_exchange'],
                opp['sell_exchange'],
                opp['buy_price'],
                opp['sell_price'],
                opp['profit_percentage']
            ))
        
        conn.commit()
        conn.close()
    
    def _log_trade(self, opportunity: Dict, result: Dict, status: str):
        """Log trade to database"""
        conn = sqlite3.connect(DATABASE_CONFIG['file'])
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades 
            (timestamp, symbol, buy_exchange, sell_exchange, buy_price, sell_price, 
             amount, profit, profit_percentage, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            opportunity['symbol'],
            opportunity['buy_exchange'],
            opportunity['sell_exchange'],
            opportunity['buy_price'],
            opportunity['sell_price'],
            opportunity['recommended_amount'],
            result.get('profit', 0),
            opportunity['profit_percentage'],
            status
        ))
        
        conn.commit()
        conn.close()
    
    async def _send_trade_notification(self, opportunity: Dict, result: Dict, success: bool):
        """Send email notification about trade"""
        if success:
            subject = f"✅ Arbitrage Trade Executed - {opportunity['symbol']}"
            message = f"""
            Successful arbitrage trade executed:
            
            Symbol: {opportunity['symbol']}
            Buy Exchange: {opportunity['buy_exchange']} @ ${opportunity['buy_price']:.4f}
            Sell Exchange: {opportunity['sell_exchange']} @ ${opportunity['sell_price']:.4f}
            Amount: ${opportunity['recommended_amount']:.2f}
            Profit: ${result['profit']:.2f} ({opportunity['profit_percentage']:.2%})
            
            Daily Volume: ${self.daily_volume:.2f} / ${TRADING_CONFIG['daily_limit']}
            """
        else:
            subject = f"❌ Arbitrage Trade Failed - {opportunity['symbol']}"
            message = f"""
            Failed arbitrage trade:
            
            Symbol: {opportunity['symbol']}
            Buy Exchange: {opportunity['buy_exchange']} @ ${opportunity['buy_price']:.4f}
            Sell Exchange: {opportunity['sell_exchange']} @ ${opportunity['sell_price']:.4f}
            Expected Profit: {opportunity['profit_percentage']:.2%}
            Error: {result.get('error', 'Unknown error')}
            """
        
        await self.email_notifier.send_notification(subject, message)
    
    def get_status(self) -> Dict:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'daily_volume': self.daily_volume,
            'daily_limit': TRADING_CONFIG['daily_limit'],
            'hourly_trades': self._get_hourly_trade_count(),
            'hourly_limit': TRADING_CONFIG['max_trades_per_hour'],
            'last_scan': datetime.now().isoformat(),
            'opportunities_found': len(self.last_opportunities),
            'exchange_status': self.exchange_manager.get_exchange_status()
        }
    
    def get_recent_opportunities(self, limit: int = 10) -> List[Dict]:
        """Get recent arbitrage opportunities"""
        conn = sqlite3.connect(DATABASE_CONFIG['file'])
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM opportunities 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'timestamp', 'symbol', 'buy_exchange', 'sell_exchange', 
                  'buy_price', 'sell_price', 'profit_percentage', 'executed']
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get trade history"""
        conn = sqlite3.connect(DATABASE_CONFIG['file'])
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trades 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'timestamp', 'symbol', 'buy_exchange', 'sell_exchange',
                  'buy_price', 'sell_price', 'amount', 'profit', 'profit_percentage', 'status']
        
        return [dict(zip(columns, row)) for row in rows]