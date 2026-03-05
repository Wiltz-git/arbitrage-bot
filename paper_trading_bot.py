"""
Paper Trading Bot - Simulates crypto arbitrage trading without executing real trades
Monitors opportunities, logs detailed information, and tracks virtual portfolio performance
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import sqlite3
from exchange_manager import ExchangeManager
from config import TRADING_CONFIG, LOGGING_CONFIG, DATABASE_CONFIG, PAPER_TRADING_CONFIG, SCALING_CONFIG


class PaperTradingBot:
    """Paper trading bot that simulates arbitrage trading without real execution"""
    
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        self.exchange_manager = ExchangeManager()
        
        # Paper trading state
        self.is_running = False
        self.virtual_balance = PAPER_TRADING_CONFIG['initial_balance']
        self.initial_balance = PAPER_TRADING_CONFIG['initial_balance']
        self.daily_simulated_volume = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.hourly_trades = []
        
        # Tracking
        self.opportunities_detected = []
        self.simulated_trades = []
        self.daily_stats = {
            'total_opportunities': 0,
            'qualified_opportunities': 0,
            'simulated_trades': 0,
            'total_profit': 0.0,
            'best_opportunity': None,
            'worst_opportunity': None,
        }
        
        # Create today's log file
        self.today_log_file = self._get_today_log_file()
        
        self.logger.info("=" * 80)
        self.logger.info("PAPER TRADING BOT INITIALIZED")
        self.logger.info(f"Mode: SIMULATION ONLY - NO REAL TRADES WILL BE EXECUTED")
        self.logger.info(f"Initial Virtual Balance: ${self.virtual_balance:.2f}")
        self.logger.info(f"Min Profit Threshold: {TRADING_CONFIG['min_profit_threshold'] * 100:.1f}%")
        
        # Log scaling configuration
        if SCALING_CONFIG['enabled']:
            max_trade, daily_limit = self.calculate_dynamic_trade_amount()
            self.logger.info(f"📊 COMPOUNDING/SCALING: ENABLED")
            self.logger.info(f"   Mode: {SCALING_CONFIG['mode']}")
            self.logger.info(f"   Trade Percentage: {SCALING_CONFIG['trade_percentage'] * 100:.1f}% of balance")
            self.logger.info(f"   Current Max Trade: ${max_trade:.2f}")
            self.logger.info(f"   Current Daily Limit: ${daily_limit:.2f}")
            self.logger.info(f"   Hard Limits: ${SCALING_CONFIG['min_trade_amount']:.0f} - ${SCALING_CONFIG['max_trade_amount']:.0f}")
        else:
            self.logger.info(f"📊 SCALING: DISABLED (fixed amounts)")
            self.logger.info(f"Max Trade Amount: ${TRADING_CONFIG['max_trade_amount']:.2f}")
            self.logger.info(f"Daily Limit: ${TRADING_CONFIG['daily_limit']:.2f}")
        self.logger.info("=" * 80)
    
    def setup_logging(self):
        """Setup enhanced logging for paper trading"""
        log_dir = PAPER_TRADING_CONFIG['log_directory']
        os.makedirs(log_dir, exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup logger
        self.logger = logging.getLogger('PaperTradingBot')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers = []  # Clear existing handlers
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler will be added per session
    
    def setup_directories(self):
        """Create necessary directories"""
        Path(PAPER_TRADING_CONFIG['log_directory']).mkdir(parents=True, exist_ok=True)
        Path('data').mkdir(parents=True, exist_ok=True)
    
    def _get_today_log_file(self) -> str:
        """Get today's log file path"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(
            PAPER_TRADING_CONFIG['log_directory'],
            f'paper_trading_log_{today}.txt'
        )
        
        # Add file handler for today's log
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(file_handler)
        
        return log_file
    
    def calculate_dynamic_trade_amount(self, recommended_amount: float = None) -> tuple[float, float]:
        """
        Calculate trade amount based on current balance and scaling configuration.
        
        Returns:
            tuple: (max_trade_amount, daily_limit) - dynamically calculated limits
        """
        if not SCALING_CONFIG['enabled']:
            # Scaling disabled - use fixed amounts from TRADING_CONFIG
            return TRADING_CONFIG['max_trade_amount'], TRADING_CONFIG['daily_limit']
        
        current_balance = self.virtual_balance
        
        # Calculate max trade amount based on scaling tier
        max_trade = SCALING_CONFIG['min_trade_amount']
        for tier in SCALING_CONFIG['scaling_tiers']:
            if current_balance >= tier['balance_threshold']:
                max_trade = tier['max_trade']
        
        # Apply percentage-based calculation if in percentage mode
        if SCALING_CONFIG['mode'] == 'percentage':
            percentage_amount = current_balance * SCALING_CONFIG['trade_percentage']
            max_trade = min(max_trade, percentage_amount)
        
        # Enforce hard limits
        max_trade = max(max_trade, SCALING_CONFIG['min_trade_amount'])
        max_trade = min(max_trade, SCALING_CONFIG['max_trade_amount'])
        
        # Calculate dynamic daily limit
        if SCALING_CONFIG['scale_daily_limit']:
            daily_limit = current_balance * SCALING_CONFIG['daily_limit_percentage']
            daily_limit = max(daily_limit, SCALING_CONFIG['min_daily_limit'])
            daily_limit = min(daily_limit, SCALING_CONFIG['max_daily_limit'])
        else:
            daily_limit = TRADING_CONFIG['daily_limit']
        
        return max_trade, daily_limit
    
    def get_scaling_status(self) -> dict:
        """Get current scaling status for logging/display"""
        max_trade, daily_limit = self.calculate_dynamic_trade_amount()
        return {
            'scaling_enabled': SCALING_CONFIG['enabled'],
            'current_balance': self.virtual_balance,
            'initial_balance': self.initial_balance,
            'growth_percentage': ((self.virtual_balance - self.initial_balance) / self.initial_balance) * 100,
            'current_max_trade': max_trade,
            'current_daily_limit': daily_limit,
            'base_max_trade': TRADING_CONFIG['max_trade_amount'],
            'base_daily_limit': TRADING_CONFIG['daily_limit'],
        }
    
    async def start(self, duration_minutes: Optional[int] = None):
        """
        Start the paper trading bot
        
        Args:
            duration_minutes: If provided, run for this many minutes then stop
        """
        self.is_running = True
        self.logger.info("\n" + "=" * 80)
        self.logger.info("STARTING PAPER TRADING SESSION")
        self.logger.info(f"Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if duration_minutes:
            self.logger.info(f"Duration: {duration_minutes} minutes")
        self.logger.info("=" * 80 + "\n")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes) if duration_minutes else None
        
        scan_count = 0
        
        try:
            while self.is_running:
                # Check if we should stop based on duration
                if end_time and datetime.now() >= end_time:
                    self.logger.info(f"\nDuration limit reached ({duration_minutes} minutes)")
                    break
                
                scan_count += 1
                await self.scan_for_opportunities(scan_count)
                await asyncio.sleep(5)  # Scan every 5 seconds
                
        except KeyboardInterrupt:
            self.logger.info("\n\nReceived keyboard interrupt - stopping...")
        except Exception as e:
            self.logger.error(f"\nError in main loop: {str(e)}", exc_info=True)
        finally:
            await self.stop()
    
    def stop(self):
        """Stop the bot and generate final report"""
        self.is_running = False
        self.logger.info("\n" + "=" * 80)
        self.logger.info("STOPPING PAPER TRADING SESSION")
        self.logger.info("=" * 80)
        
        # Generate session summary
        self._generate_session_summary()
        
        # Generate daily summary if enabled
        if PAPER_TRADING_CONFIG['daily_summary_enabled']:
            self._generate_daily_summary()
    
    async def scan_for_opportunities(self, scan_number: int):
        """Scan for arbitrage opportunities and simulate trading"""
        # Reset daily volume if needed
        self._check_daily_reset()
        
        self.logger.info(f"\n--- Scan #{scan_number} at {datetime.now().strftime('%H:%M:%S')} ---")
        
        opportunities_this_scan = []
        
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
                    opportunities_this_scan.append(opp)
                    
                    # Log detailed opportunity information
                    self._log_opportunity_details(opp)
                
            except Exception as e:
                self.logger.error(f"Error scanning {symbol}: {str(e)}")
        
        # Process opportunities
        if opportunities_this_scan:
            self.logger.info(f"\n✓ Found {len(opportunities_this_scan)} opportunities in this scan")
            
            # Track all opportunities
            self.opportunities_detected.extend(opportunities_this_scan)
            self.daily_stats['total_opportunities'] += len(opportunities_this_scan)
            
            # Find best opportunity
            best_opp = max(opportunities_this_scan, key=lambda x: x['profit_percentage'])
            
            # Check if it meets criteria and should be "executed"
            if self._should_simulate_trade(best_opp):
                await self._simulate_trade(best_opp)
        else:
            self.logger.info("No opportunities detected in this scan")
    
    def _log_opportunity_details(self, opp: Dict):
        """Log detailed information about an opportunity"""
        profit_pct = opp['profit_percentage'] * 100
        meets_threshold = opp['profit_percentage'] >= TRADING_CONFIG['min_profit_threshold']
        
        # Get dynamic trade limits
        max_trade_amount, daily_limit = self.calculate_dynamic_trade_amount()
        
        # Calculate estimated fees and net profit
        trade_amount = min(opp['recommended_amount'], max_trade_amount)
        estimated_fees = trade_amount * TRADING_CONFIG['fee_buffer']
        gross_profit = trade_amount * opp['profit_percentage']
        net_profit = gross_profit - estimated_fees
        
        self.logger.info(f"\n  📊 OPPORTUNITY DETECTED: {opp['symbol']}")
        self.logger.info(f"     Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"     Buy:  {opp['buy_exchange']: <12} @ ${opp['buy_price']:.4f}")
        self.logger.info(f"     Sell: {opp['sell_exchange']: <12} @ ${opp['sell_price']:.4f}")
        self.logger.info(f"     Profit: {profit_pct:.3f}% {'✓ MEETS THRESHOLD' if meets_threshold else '✗ Below threshold'}")
        self.logger.info(f"     Trade Amount: ${trade_amount:.2f} (max: ${max_trade_amount:.2f})")
        self.logger.info(f"     Estimated Fees: ${estimated_fees:.2f}")
        self.logger.info(f"     Net Profit: ${net_profit:.2f}")
        
        # Track best and worst opportunities
        if meets_threshold:
            self.daily_stats['qualified_opportunities'] += 1
            
            if (self.daily_stats['best_opportunity'] is None or 
                opp['profit_percentage'] > self.daily_stats['best_opportunity']['profit_percentage']):
                self.daily_stats['best_opportunity'] = opp.copy()
                self.daily_stats['best_opportunity']['net_profit'] = net_profit
            
            if (self.daily_stats['worst_opportunity'] is None or 
                opp['profit_percentage'] < self.daily_stats['worst_opportunity']['profit_percentage']):
                self.daily_stats['worst_opportunity'] = opp.copy()
                self.daily_stats['worst_opportunity']['net_profit'] = net_profit
    
    def _should_simulate_trade(self, opportunity: Dict) -> bool:
        """Determine if a simulated trade should be executed"""
        # Check profit threshold
        if opportunity['profit_percentage'] < TRADING_CONFIG['min_profit_threshold']:
            return False
        
        # Get dynamic trade limits
        max_trade_amount, daily_limit = self.calculate_dynamic_trade_amount()
        
        # Check if we have enough virtual balance
        trade_amount = min(opportunity['recommended_amount'], max_trade_amount)
        min_trade = SCALING_CONFIG['min_trade_amount'] if SCALING_CONFIG['enabled'] else 10
        if trade_amount < min_trade:
            return False
        
        if self.virtual_balance < trade_amount:
            self.logger.warning(f"⚠️  Insufficient virtual balance: ${self.virtual_balance:.2f} < ${trade_amount:.2f}")
            return False
        
        # Check daily volume limit (dynamic)
        if self.daily_simulated_volume + trade_amount > daily_limit:
            self.logger.info(f"⚠️  Daily limit reached: ${self.daily_simulated_volume:.2f} / ${daily_limit:.2f}")
            return False
        
        # Check hourly trade limit
        if self._get_hourly_trade_count() >= TRADING_CONFIG['max_trades_per_hour']:
            self.logger.info(f"⚠️  Hourly trade limit reached: {self._get_hourly_trade_count()} / {TRADING_CONFIG['max_trades_per_hour']}")
            return False
        
        return True
    
    async def _simulate_trade(self, opportunity: Dict):
        """Simulate executing an arbitrage trade"""
        # Get dynamic trade limits
        max_trade_amount, daily_limit = self.calculate_dynamic_trade_amount()
        trade_amount = min(opportunity['recommended_amount'], max_trade_amount)
        
        self.logger.info(f"\n  {'=' * 76}")
        self.logger.info(f"  🎯 SIMULATING TRADE: {opportunity['symbol']}")
        self.logger.info(f"  {'=' * 76}")
        self.logger.info(f"  WOULD BUY:  ${trade_amount:.2f} on {opportunity['buy_exchange']} @ ${opportunity['buy_price']:.4f}")
        self.logger.info(f"  WOULD SELL: ${trade_amount:.2f} on {opportunity['sell_exchange']} @ ${opportunity['sell_price']:.4f}")
        
        # Calculate simulated profit
        estimated_fees = trade_amount * TRADING_CONFIG['fee_buffer']
        gross_profit = trade_amount * opportunity['profit_percentage']
        net_profit = gross_profit - estimated_fees
        
        self.logger.info(f"\n  📈 SIMULATED RESULTS:")
        self.logger.info(f"     Trade Amount: ${trade_amount:.2f} (scaled max: ${max_trade_amount:.2f})")
        self.logger.info(f"     Gross Profit: ${gross_profit:.2f} ({opportunity['profit_percentage'] * 100:.2f}%)")
        self.logger.info(f"     Estimated Fees: ${estimated_fees:.2f}")
        self.logger.info(f"     Net Profit: ${net_profit:.2f}")
        
        # Update virtual balance
        old_balance = self.virtual_balance
        self.virtual_balance += net_profit
        
        # Log scaling info if enabled
        scaling_status = self.get_scaling_status()
        self.logger.info(f"\n  💰 VIRTUAL PORTFOLIO:")
        self.logger.info(f"     Previous Balance: ${old_balance:.2f}")
        self.logger.info(f"     New Balance: ${self.virtual_balance:.2f}")
        self.logger.info(f"     Total P&L: ${self.virtual_balance - self.initial_balance:.2f} ({scaling_status['growth_percentage']:.2f}%)")
        if SCALING_CONFIG['enabled']:
            new_max_trade, new_daily_limit = self.calculate_dynamic_trade_amount()
            self.logger.info(f"     📊 SCALING: Next max trade: ${new_max_trade:.2f}, Daily limit: ${new_daily_limit:.2f}")
        self.logger.info(f"  {'=' * 76}\n")
        
        # Update tracking
        self.daily_simulated_volume += trade_amount
        self.hourly_trades.append(datetime.now())
        self.daily_stats['simulated_trades'] += 1
        self.daily_stats['total_profit'] += net_profit
        
        # Record the simulated trade
        simulated_trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': opportunity['symbol'],
            'buy_exchange': opportunity['buy_exchange'],
            'sell_exchange': opportunity['sell_exchange'],
            'buy_price': opportunity['buy_price'],
            'sell_price': opportunity['sell_price'],
            'trade_amount': trade_amount,
            'gross_profit': gross_profit,
            'fees': estimated_fees,
            'net_profit': net_profit,
            'profit_percentage': opportunity['profit_percentage'],
            'balance_after': self.virtual_balance,
            'scaling_enabled': SCALING_CONFIG['enabled'],
            'max_trade_at_time': max_trade_amount,
            'daily_limit_at_time': daily_limit,
            'status': 'executed'
        }
        self.simulated_trades.append(simulated_trade)
        
        # Save to JSON file
        self._save_simulated_trade(simulated_trade)
    
    def _save_simulated_trade(self, trade: Dict):
        """Save simulated trade to JSON file and sync to dashboard"""
        trades_file = os.path.join(
            PAPER_TRADING_CONFIG['log_directory'],
            f"simulated_trades_{datetime.now().strftime('%Y-%m-%d')}.json"
        )
        
        trades = []
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades = json.load(f)
        
        trades.append(trade)
        
        with open(trades_file, 'w') as f:
            json.dump(trades, f, indent=2)
        
        # Sync trade to remote dashboard
        try:
            from dashboard_sync import sync_trade
            if sync_trade(trade):
                self.logger.info("  📡 Trade synced to dashboard")
        except ImportError:
            pass  # Dashboard sync module not available
        except Exception as e:
            self.logger.warning(f"  ⚠️ Dashboard sync failed: {e}")
    
    def _check_daily_reset(self):
        """Check if we need to reset daily volume and stats"""
        now = datetime.now()
        if now.date() > self.daily_reset_time.date():
            # Generate daily summary before reset
            if PAPER_TRADING_CONFIG['daily_summary_enabled']:
                self._generate_daily_summary()
            
            # Reset daily tracking
            self.daily_simulated_volume = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            self.daily_stats = {
                'total_opportunities': 0,
                'qualified_opportunities': 0,
                'simulated_trades': 0,
                'total_profit': 0.0,
                'best_opportunity': None,
                'worst_opportunity': None,
            }
            self.opportunities_detected = []
            self.simulated_trades = []
            
            # Create new log file for the new day
            self.today_log_file = self._get_today_log_file()
            
            self.logger.info("\n" + "=" * 80)
            self.logger.info("NEW TRADING DAY - Daily stats reset")
            self.logger.info("=" * 80 + "\n")
    
    def _get_hourly_trade_count(self) -> int:
        """Get number of simulated trades in the last hour"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        self.hourly_trades = [t for t in self.hourly_trades if t > hour_ago]
        return len(self.hourly_trades)
    
    def _generate_session_summary(self):
        """Generate summary of the current session"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("SESSION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Session End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"\nOpportunities:")
        self.logger.info(f"  Total Detected: {self.daily_stats['total_opportunities']}")
        self.logger.info(f"  Met Criteria (≥1.5%): {self.daily_stats['qualified_opportunities']}")
        self.logger.info(f"  Simulated Trades: {self.daily_stats['simulated_trades']}")
        
        if self.simulated_trades:
            self.logger.info(f"\nTrading Performance:")
            self.logger.info(f"  Total Simulated Profit: ${self.daily_stats['total_profit']:.2f}")
            self.logger.info(f"  Average Profit per Trade: ${self.daily_stats['total_profit'] / self.daily_stats['simulated_trades']:.2f}")
            self.logger.info(f"\nPortfolio:")
            self.logger.info(f"  Starting Balance: ${self.initial_balance:.2f}")
            self.logger.info(f"  Current Balance: ${self.virtual_balance:.2f}")
            self.logger.info(f"  Total P&L: ${self.virtual_balance - self.initial_balance:.2f}")
            self.logger.info(f"  Return: {((self.virtual_balance / self.initial_balance - 1) * 100):.2f}%")
        
        if self.daily_stats['best_opportunity']:
            best = self.daily_stats['best_opportunity']
            self.logger.info(f"\nBest Opportunity:")
            self.logger.info(f"  {best['symbol']} - {best['profit_percentage'] * 100:.2f}%")
            self.logger.info(f"  {best['buy_exchange']} → {best['sell_exchange']}")
            self.logger.info(f"  Net Profit: ${best.get('net_profit', 0):.2f}")
        
        if self.daily_stats['worst_opportunity'] and self.daily_stats['qualified_opportunities'] > 1:
            worst = self.daily_stats['worst_opportunity']
            self.logger.info(f"\nWorst Qualified Opportunity:")
            self.logger.info(f"  {worst['symbol']} - {worst['profit_percentage'] * 100:.2f}%")
            self.logger.info(f"  {worst['buy_exchange']} → {worst['sell_exchange']}")
            self.logger.info(f"  Net Profit: ${worst.get('net_profit', 0):.2f}")
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info(f"Detailed logs saved to: {self.today_log_file}")
        self.logger.info("=" * 80 + "\n")
    
    def _generate_daily_summary(self):
        """Generate daily summary report"""
        today = datetime.now().strftime('%Y-%m-%d')
        summary_file = os.path.join(
            PAPER_TRADING_CONFIG['log_directory'],
            f'daily_summary_{today}.txt'
        )
        
        with open(summary_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"DAILY PAPER TRADING SUMMARY - {today}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("OVERVIEW\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Opportunities Detected: {self.daily_stats['total_opportunities']}\n")
            f.write(f"Opportunities Meeting Criteria (≥1.5%): {self.daily_stats['qualified_opportunities']}\n")
            f.write(f"Simulated Trades Executed: {self.daily_stats['simulated_trades']}\n\n")
            
            if self.simulated_trades:
                f.write("TRADING PERFORMANCE\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Simulated Profit: ${self.daily_stats['total_profit']:.2f}\n")
                f.write(f"Average Profit per Trade: ${self.daily_stats['total_profit'] / self.daily_stats['simulated_trades']:.2f}\n")
                f.write(f"Starting Virtual Balance: ${self.initial_balance:.2f}\n")
                f.write(f"Ending Virtual Balance: ${self.virtual_balance:.2f}\n")
                f.write(f"Total P&L: ${self.virtual_balance - self.initial_balance:.2f}\n")
                f.write(f"Return on Investment: {((self.virtual_balance / self.initial_balance - 1) * 100):.2f}%\n\n")
                
                f.write("SIMULATED TRADES\n")
                f.write("-" * 80 + "\n")
                for i, trade in enumerate(self.simulated_trades, 1):
                    f.write(f"\nTrade #{i}:\n")
                    f.write(f"  Time: {trade['timestamp']}\n")
                    f.write(f"  Symbol: {trade['symbol']}\n")
                    f.write(f"  Buy: {trade['buy_exchange']} @ ${trade['buy_price']:.4f}\n")
                    f.write(f"  Sell: {trade['sell_exchange']} @ ${trade['sell_price']:.4f}\n")
                    f.write(f"  Amount: ${trade['trade_amount']:.2f}\n")
                    f.write(f"  Profit: ${trade['net_profit']:.2f} ({trade['profit_percentage'] * 100:.2f}%)\n")
            
            if self.daily_stats['best_opportunity']:
                best = self.daily_stats['best_opportunity']
                f.write("\nBEST OPPORTUNITY OF THE DAY\n")
                f.write("-" * 80 + "\n")
                f.write(f"Symbol: {best['symbol']}\n")
                f.write(f"Profit: {best['profit_percentage'] * 100:.2f}%\n")
                f.write(f"Route: {best['buy_exchange']} → {best['sell_exchange']}\n")
                f.write(f"Buy Price: ${best['buy_price']:.4f}\n")
                f.write(f"Sell Price: ${best['sell_price']:.4f}\n")
                f.write(f"Net Profit: ${best.get('net_profit', 0):.2f}\n")
            
            if self.daily_stats['worst_opportunity']:
                worst = self.daily_stats['worst_opportunity']
                f.write("\nWORST QUALIFIED OPPORTUNITY OF THE DAY\n")
                f.write("-" * 80 + "\n")
                f.write(f"Symbol: {worst['symbol']}\n")
                f.write(f"Profit: {worst['profit_percentage'] * 100:.2f}%\n")
                f.write(f"Route: {worst['buy_exchange']} → {worst['sell_exchange']}\n")
                f.write(f"Buy Price: ${worst['buy_price']:.4f}\n")
                f.write(f"Sell Price: ${worst['sell_price']:.4f}\n")
                f.write(f"Net Profit: ${worst.get('net_profit', 0):.2f}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("End of Daily Summary\n")
            f.write("=" * 80 + "\n")
        
        self.logger.info(f"\n📊 Daily summary report saved to: {summary_file}")
    
    def get_status(self) -> Dict:
        """Get current bot status"""
        return {
            'mode': 'PAPER_TRADING',
            'is_running': self.is_running,
            'virtual_balance': self.virtual_balance,
            'initial_balance': self.initial_balance,
            'total_pnl': self.virtual_balance - self.initial_balance,
            'return_percentage': ((self.virtual_balance / self.initial_balance - 1) * 100),
            'daily_volume': self.daily_simulated_volume,
            'daily_limit': TRADING_CONFIG['daily_limit'],
            'opportunities_detected': self.daily_stats['total_opportunities'],
            'qualified_opportunities': self.daily_stats['qualified_opportunities'],
            'simulated_trades': self.daily_stats['simulated_trades'],
            'total_profit': self.daily_stats['total_profit'],
        }


async def main():
    """Main entry point for paper trading bot"""
    bot = PaperTradingBot()
    
    try:
        # Run for a specified duration or indefinitely
        await bot.start(duration_minutes=None)  # Set to None to run indefinitely
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
