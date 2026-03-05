#!/usr/bin/env python3
"""
Demo Arbitrage Monitor - Simulates arbitrage opportunities for demonstration
"""

import json
import time
import random
from datetime import datetime, timedelta
import sqlite3

class DemoArbitrageMonitor:
    def __init__(self):
        self.opportunities = []
        self.price_data = []
        self.session_start = datetime.now()
        self.trades_executed = 0
        self.total_profit = 0
        
        # Demo cryptocurrency prices (approximate current values)
        self.base_prices = {
            'BTC/USDT': 109000,
            'ETH/USDT': 4530,
            'BNB/USDT': 854,
            'ADA/USDT': 1.45,
            'SOL/USDT': 245,
            'DOT/USDT': 12.5
        }
        
        self.exchanges = ['kraken', 'kucoin', 'binance', 'coinbase']
        
    def generate_price_data(self, symbol):
        """Generate realistic price data with small variations"""
        base_price = self.base_prices[symbol]
        
        prices = {}
        for exchange in self.exchanges:
            # Add small random variations (±0.5%)
            variation = random.uniform(-0.005, 0.005)
            price = base_price * (1 + variation)
            
            # Add bid-ask spread (0.01-0.05%)
            spread = random.uniform(0.0001, 0.0005)
            bid = price * (1 - spread/2)
            ask = price * (1 + spread/2)
            
            prices[exchange] = {
                'bid': round(bid, 2 if base_price > 100 else 4),
                'ask': round(ask, 2 if base_price > 100 else 4)
            }
            
        return prices
    
    def find_arbitrage_opportunities(self, symbol, prices):
        """Find arbitrage opportunities between exchanges"""
        opportunities = []
        
        for buy_exchange in self.exchanges:
            for sell_exchange in self.exchanges:
                if buy_exchange == sell_exchange:
                    continue
                    
                if buy_exchange not in prices or sell_exchange not in prices:
                    continue
                    
                buy_price = prices[buy_exchange]['ask']
                sell_price = prices[sell_exchange]['bid']
                
                # Calculate profit percentage (accounting for fees)
                fee_rate = 0.002  # 0.2% total fees
                profit_pct = (sell_price - buy_price) / buy_price - fee_rate
                
                if profit_pct > 0.015:  # 1.5% minimum profit threshold
                    opportunity = {
                        'symbol': symbol,
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'profit_pct': profit_pct * 100,
                        'profit_usd': profit_pct * 1000,  # Assuming $1000 trade
                        'timestamp': datetime.now().isoformat()
                    }
                    opportunities.append(opportunity)
                    
        return opportunities
    
    def simulate_trade_execution(self, opportunity):
        """Simulate executing a trade"""
        trade_amount = 1000  # $1000 per trade
        profit = opportunity['profit_usd']
        
        trade_record = {
            'id': len(self.opportunities) + 1,
            'timestamp': opportunity['timestamp'],
            'symbol': opportunity['symbol'],
            'buy_exchange': opportunity['buy_exchange'],
            'sell_exchange': opportunity['sell_exchange'],
            'buy_price': opportunity['buy_price'],
            'sell_price': opportunity['sell_price'],
            'amount_usd': trade_amount,
            'profit_usd': profit,
            'profit_pct': opportunity['profit_pct'],
            'status': 'executed'
        }
        
        self.trades_executed += 1
        self.total_profit += profit
        
        return trade_record
    
    def run_monitoring_session(self, duration_minutes=55):
        """Run monitoring session for specified duration"""
        print(f"Starting Demo Arbitrage Monitor for {duration_minutes} minutes...")
        print("Monitoring exchanges: kraken, kucoin, binance, coinbase")
        print("Cryptocurrencies: BTC/USDT, ETH/USDT, BNB/USDT, ADA/USDT, SOL/USDT, DOT/USDT")
        print("-" * 60)
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        scan_count = 0
        
        while datetime.now() < end_time:
            scan_count += 1
            print(f"\nScan #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            for symbol in self.base_prices.keys():
                # Generate price data
                prices = self.generate_price_data(symbol)
                
                price_entry = {
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat(),
                    'prices': prices
                }
                self.price_data.append(price_entry)
                
                # Find opportunities
                opportunities = self.find_arbitrage_opportunities(symbol, prices)
                
                for opp in opportunities:
                    print(f"🚀 OPPORTUNITY: {opp['symbol']} - Buy on {opp['buy_exchange']} at ${opp['buy_price']}, Sell on {opp['sell_exchange']} at ${opp['sell_price']} - Profit: {opp['profit_pct']:.2f}% (${opp['profit_usd']:.2f})")
                    
                    # Simulate trade execution
                    trade = self.simulate_trade_execution(opp)
                    self.opportunities.append(trade)
                    
                    print(f"✅ TRADE EXECUTED: {trade['symbol']} - Profit: ${trade['profit_usd']:.2f}")
            
            # Wait before next scan (every 10 seconds for demo)
            time.sleep(10)
            
        print(f"\n" + "="*60)
        print("MONITORING SESSION COMPLETE")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Total scans: {scan_count}")
        print(f"Trades executed: {self.trades_executed}")
        print(f"Total profit: ${self.total_profit:.2f}")
        print(f"Average profit per trade: ${self.total_profit/max(1, self.trades_executed):.2f}")
        
        return self.generate_session_report()
    
    def generate_session_report(self):
        """Generate comprehensive session report"""
        report = {
            'session_info': {
                'start_time': self.session_start.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': (datetime.now() - self.session_start).total_seconds() / 60,
                'total_scans': len(self.price_data) // len(self.base_prices),
                'symbols_monitored': list(self.base_prices.keys()),
                'exchanges_monitored': self.exchanges,
                'trades_executed': self.trades_executed,
                'total_profit_usd': round(self.total_profit, 2),
                'average_profit_per_trade': round(self.total_profit/max(1, self.trades_executed), 2)
            },
            'trades': self.opportunities,
            'price_samples': self.price_data[-50:],  # Last 50 price samples
            'summary_stats': {
                'most_profitable_pair': self.get_most_profitable_pair(),
                'best_exchange_combination': self.get_best_exchange_combo(),
                'hourly_profit_rate': round(self.total_profit * (60 / max(1, (datetime.now() - self.session_start).total_seconds() / 60)), 2)
            }
        }
        
        return report
    
    def get_most_profitable_pair(self):
        """Get the most profitable trading pair"""
        if not self.opportunities:
            return None
            
        pair_profits = {}
        for trade in self.opportunities:
            symbol = trade['symbol']
            if symbol not in pair_profits:
                pair_profits[symbol] = 0
            pair_profits[symbol] += trade['profit_usd']
            
        return max(pair_profits.items(), key=lambda x: x[1]) if pair_profits else None
    
    def get_best_exchange_combo(self):
        """Get the best exchange combination"""
        if not self.opportunities:
            return None
            
        combo_profits = {}
        for trade in self.opportunities:
            combo = f"{trade['buy_exchange']} -> {trade['sell_exchange']}"
            if combo not in combo_profits:
                combo_profits[combo] = 0
            combo_profits[combo] += trade['profit_usd']
            
        return max(combo_profits.items(), key=lambda x: x[1]) if combo_profits else None

if __name__ == "__main__":
    monitor = DemoArbitrageMonitor()
    report = monitor.run_monitoring_session(55)  # Run for 55 minutes
    
    # Save report to file
    with open('demo_arbitrage_results.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Full report saved to: demo_arbitrage_results.json")
