"""
Demo Paper Trading Bot - Uses mock data to demonstrate paper trading functionality
Shows how the bot detects opportunities and simulates trades without real execution
"""

import asyncio
import logging
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class DemoPaperTradingBot:
    """Demo paper trading bot with mock data"""
    
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        
        # Paper trading state
        self.virtual_balance = 1000.0
        self.initial_balance = 1000.0
        self.min_profit_threshold = 0.015  # 1.5%
        self.max_trade_amount = 10.0
        self.daily_limit = 50.0
        
        self.daily_simulated_volume = 0
        self.simulated_trades = []
        self.daily_stats = {
            'total_opportunities': 0,
            'qualified_opportunities': 0,
            'simulated_trades': 0,
            'total_profit': 0.0,
            'best_opportunity': None,
            'worst_opportunity': None,
        }
        
        self.today_log_file = self._get_today_log_file()
        
        self.logger.info("=" * 80)
        self.logger.info("DEMO PAPER TRADING BOT INITIALIZED")
        self.logger.info(f"Mode: SIMULATION ONLY - NO REAL TRADES WILL BE EXECUTED")
        self.logger.info(f"Initial Virtual Balance: ${self.virtual_balance:.2f}")
        self.logger.info(f"Min Profit Threshold: {self.min_profit_threshold * 100:.1f}%")
        self.logger.info(f"Max Trade Amount: ${self.max_trade_amount:.2f}")
        self.logger.info(f"Daily Limit: ${self.daily_limit:.2f}")
        self.logger.info("=" * 80)
    
    def setup_logging(self):
        """Setup logging"""
        os.makedirs('paper_trading_logs', exist_ok=True)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.logger = logging.getLogger('DemoPaperTradingBot')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers = []
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def setup_directories(self):
        """Create directories"""
        Path('paper_trading_logs').mkdir(parents=True, exist_ok=True)
    
    def _get_today_log_file(self) -> str:
        """Get today's log file"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = f'paper_trading_logs/paper_trading_log_{today}.txt'
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(file_handler)
        
        return log_file
    
    def generate_mock_opportunity(self) -> Dict:
        """Generate a mock arbitrage opportunity"""
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT']
        exchanges = ['Kraken', 'Coinbase', 'Bitstamp', 'Crypto.com']
        
        symbol = random.choice(symbols)
        buy_exchange = random.choice(exchanges)
        sell_exchange = random.choice([e for e in exchanges if e != buy_exchange])
        
        # Generate realistic prices
        base_prices = {
            'BTC/USDT': 95000,
            'ETH/USDT': 3500,
            'BNB/USDT': 650,
            'ADA/USDT': 1.2,
            'SOL/USDT': 180
        }
        
        base_price = base_prices[symbol]
        
        # Generate profit percentage (mix of opportunities above and below threshold)
        if random.random() < 0.4:  # 40% chance of meeting threshold
            profit_pct = random.uniform(0.015, 0.035)  # 1.5% to 3.5%
        else:
            profit_pct = random.uniform(0.005, 0.014)  # 0.5% to 1.4%
        
        buy_price = base_price * random.uniform(0.998, 1.002)
        sell_price = buy_price * (1 + profit_pct)
        
        return {
            'symbol': symbol,
            'buy_exchange': buy_exchange,
            'sell_exchange': sell_exchange,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'profit_percentage': profit_pct,
            'recommended_amount': 10.0,
            'timestamp': datetime.now().isoformat()
        }
    
    async def run_demo(self, duration_minutes: int = 2):
        """Run demo for specified duration"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("STARTING DEMO PAPER TRADING SESSION")
        self.logger.info(f"Duration: {duration_minutes} minutes")
        self.logger.info(f"Scan interval: 8 seconds")
        self.logger.info("=" * 80 + "\n")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        scan_count = 0
        
        while datetime.now() < end_time:
            scan_count += 1
            await self.scan_for_opportunities(scan_count)
            await asyncio.sleep(8)
        
        self._generate_session_summary()
    
    async def scan_for_opportunities(self, scan_number: int):
        """Scan for opportunities"""
        self.logger.info(f"\n--- Scan #{scan_number} at {datetime.now().strftime('%H:%M:%S')} ---")
        
        # Generate 1-3 mock opportunities per scan
        num_opportunities = random.randint(1, 3) if random.random() < 0.7 else 0
        
        if num_opportunities == 0:
            self.logger.info("No opportunities detected in this scan")
            return
        
        opportunities = [self.generate_mock_opportunity() for _ in range(num_opportunities)]
        
        self.logger.info(f"\n✓ Found {len(opportunities)} opportunities in this scan")
        
        for opp in opportunities:
            self._log_opportunity_details(opp)
        
        # Try to execute the best one
        best_opp = max(opportunities, key=lambda x: x['profit_percentage'])
        
        if self._should_simulate_trade(best_opp):
            await self._simulate_trade(best_opp)
    
    def _log_opportunity_details(self, opp: Dict):
        """Log detailed opportunity information"""
        profit_pct = opp['profit_percentage'] * 100
        meets_threshold = opp['profit_percentage'] >= self.min_profit_threshold
        
        trade_amount = min(opp['recommended_amount'], self.max_trade_amount)
        fee_buffer = 0.002  # 0.2%
        estimated_fees = trade_amount * fee_buffer
        gross_profit = trade_amount * opp['profit_percentage']
        net_profit = gross_profit - estimated_fees
        
        self.logger.info(f"\n  📊 OPPORTUNITY DETECTED: {opp['symbol']}")
        self.logger.info(f"     Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"     Buy:  {opp['buy_exchange']: <12} @ ${opp['buy_price']:.4f}")
        self.logger.info(f"     Sell: {opp['sell_exchange']: <12} @ ${opp['sell_price']:.4f}")
        self.logger.info(f"     Profit: {profit_pct:.3f}% {'✓ MEETS THRESHOLD' if meets_threshold else '✗ Below threshold'}")
        self.logger.info(f"     Trade Amount: ${trade_amount:.2f}")
        self.logger.info(f"     Estimated Fees: ${estimated_fees:.2f}")
        self.logger.info(f"     Net Profit: ${net_profit:.2f}")
        
        self.daily_stats['total_opportunities'] += 1
        
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
        """Check if trade should be simulated"""
        if opportunity['profit_percentage'] < self.min_profit_threshold:
            return False
        
        trade_amount = min(opportunity['recommended_amount'], self.max_trade_amount)
        
        if self.virtual_balance < trade_amount:
            self.logger.warning(f"⚠️  Insufficient virtual balance")
            return False
        
        if self.daily_simulated_volume + trade_amount > self.daily_limit:
            self.logger.info(f"⚠️  Daily limit reached")
            return False
        
        return True
    
    async def _simulate_trade(self, opportunity: Dict):
        """Simulate a trade"""
        trade_amount = min(opportunity['recommended_amount'], self.max_trade_amount)
        
        self.logger.info(f"\n  {'=' * 76}")
        self.logger.info(f"  🎯 SIMULATING TRADE: {opportunity['symbol']}")
        self.logger.info(f"  {'=' * 76}")
        self.logger.info(f"  WOULD BUY:  ${trade_amount:.2f} on {opportunity['buy_exchange']} @ ${opportunity['buy_price']:.4f}")
        self.logger.info(f"  WOULD SELL: ${trade_amount:.2f} on {opportunity['sell_exchange']} @ ${opportunity['sell_price']:.4f}")
        
        fee_buffer = 0.002
        estimated_fees = trade_amount * fee_buffer
        gross_profit = trade_amount * opportunity['profit_percentage']
        net_profit = gross_profit - estimated_fees
        
        self.logger.info(f"\n  📈 SIMULATED RESULTS:")
        self.logger.info(f"     Trade Amount: ${trade_amount:.2f}")
        self.logger.info(f"     Gross Profit: ${gross_profit:.2f} ({opportunity['profit_percentage'] * 100:.2f}%)")
        self.logger.info(f"     Estimated Fees: ${estimated_fees:.2f}")
        self.logger.info(f"     Net Profit: ${net_profit:.2f}")
        
        old_balance = self.virtual_balance
        self.virtual_balance += net_profit
        
        self.logger.info(f"\n  💰 VIRTUAL PORTFOLIO:")
        self.logger.info(f"     Previous Balance: ${old_balance:.2f}")
        self.logger.info(f"     New Balance: ${self.virtual_balance:.2f}")
        self.logger.info(f"     Total P&L: ${self.virtual_balance - self.initial_balance:.2f} ({((self.virtual_balance / self.initial_balance - 1) * 100):.2f}%)")
        self.logger.info(f"  {'=' * 76}\n")
        
        self.daily_simulated_volume += trade_amount
        self.daily_stats['simulated_trades'] += 1
        self.daily_stats['total_profit'] += net_profit
        
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
            'balance_after': self.virtual_balance
        }
        self.simulated_trades.append(simulated_trade)
        
        # Save to file
        trades_file = f"paper_trading_logs/simulated_trades_{datetime.now().strftime('%Y-%m-%d')}.json"
        trades = []
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades = json.load(f)
        trades.append(simulated_trade)
        with open(trades_file, 'w') as f:
            json.dump(trades, f, indent=2)
    
    def _generate_session_summary(self):
        """Generate session summary"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("SESSION SUMMARY")
        self.logger.info("=" * 80)
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
        
        if self.daily_stats['worst_opportunity']:
            worst = self.daily_stats['worst_opportunity']
            self.logger.info(f"\nWorst Qualified Opportunity:")
            self.logger.info(f"  {worst['symbol']} - {worst['profit_percentage'] * 100:.2f}%")
            self.logger.info(f"  {worst['buy_exchange']} → {worst['sell_exchange']}")
            self.logger.info(f"  Net Profit: ${worst.get('net_profit', 0):.2f}")
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info(f"Detailed logs saved to: {self.today_log_file}")
        self.logger.info("=" * 80 + "\n")
        
        # Also create daily summary file
        self._generate_daily_summary()
    
    def _generate_daily_summary(self):
        """Generate daily summary file"""
        today = datetime.now().strftime('%Y-%m-%d')
        summary_file = f'paper_trading_logs/daily_summary_{today}.txt'
        
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
            
            f.write("\n" + "=" * 80 + "\n")
        
        self.logger.info(f"📊 Daily summary saved to: {summary_file}")


async def main():
    """Run demo"""
    print("\n" + "=" * 80)
    print("DEMO PAPER TRADING BOT")
    print("=" * 80)
    print("\nThis demo uses MOCK DATA to show paper trading functionality.")
    print("No real exchange connections are made.")
    print("No real trades are executed.")
    print("\nPress Ctrl+C to stop early.\n")
    print("=" * 80 + "\n")
    
    bot = DemoPaperTradingBot()
    
    try:
        await bot.run_demo(duration_minutes=2)
    except KeyboardInterrupt:
        print("\n\nDemo stopped by user")
        bot._generate_session_summary()


if __name__ == "__main__":
    asyncio.run(main())
