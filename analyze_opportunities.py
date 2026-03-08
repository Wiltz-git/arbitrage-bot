#!/usr/bin/env python3
"""
Analyze arbitrage opportunities from monitoring data
"""

import json
import os
from datetime import datetime

def analyze_price_data():
    """Analyze the monitoring log for arbitrage opportunities"""
    
    opportunities = []
    total_scans = 0
    
    # Read the monitoring log
    log_file = 'monitoring_log.json'
    if not os.path.exists(log_file):
        print("No monitoring log found")
        return
    
    print("Analyzing price data for arbitrage opportunities...")
    print("=" * 60)
    
    with open(log_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                total_scans += 1
                
                timestamp = data['timestamp']
                prices = data['prices']
                
                # Check each cryptocurrency
                for symbol, exchange_prices in prices.items():
                    if len(exchange_prices) >= 2:  # Need at least 2 exchanges
                        exchanges = list(exchange_prices.keys())
                        
                        # Compare all exchange pairs
                        for i in range(len(exchanges)):
                            for j in range(i + 1, len(exchanges)):
                                ex1, ex2 = exchanges[i], exchanges[j]
                                
                                # Get bid/ask prices
                                ex1_bid = exchange_prices[ex1]['bid']
                                ex1_ask = exchange_prices[ex1]['ask']
                                ex2_bid = exchange_prices[ex2]['bid']
                                ex2_ask = exchange_prices[ex2]['ask']
                                
                                # Calculate potential profit (buy low, sell high)
                                # Scenario 1: Buy on ex1, sell on ex2
                                if ex2_bid > ex1_ask:
                                    profit_pct = ((ex2_bid - ex1_ask) / ex1_ask) * 100
                                    if profit_pct > 0.1:  # More than 0.1% profit
                                        opportunities.append({
                                            'timestamp': timestamp,
                                            'symbol': symbol,
                                            'buy_exchange': ex1,
                                            'sell_exchange': ex2,
                                            'buy_price': ex1_ask,
                                            'sell_price': ex2_bid,
                                            'profit_pct': profit_pct
                                        })
                                
                                # Scenario 2: Buy on ex2, sell on ex1
                                if ex1_bid > ex2_ask:
                                    profit_pct = ((ex1_bid - ex2_ask) / ex2_ask) * 100
                                    if profit_pct > 0.1:  # More than 0.1% profit
                                        opportunities.append({
                                            'timestamp': timestamp,
                                            'symbol': symbol,
                                            'buy_exchange': ex2,
                                            'sell_exchange': ex1,
                                            'buy_price': ex2_ask,
                                            'sell_price': ex1_bid,
                                            'profit_pct': profit_pct
                                        })
                                        
            except json.JSONDecodeError:
                continue
    
    print(f"Total price scans analyzed: {total_scans}")
    print(f"Arbitrage opportunities found: {len(opportunities)}")
    print()
    
    if opportunities:
        # Sort by profit percentage
        opportunities.sort(key=lambda x: x['profit_pct'], reverse=True)
        
        print("Top 10 Arbitrage Opportunities:")
        print("-" * 80)
        print(f"{'Time':<20} {'Symbol':<10} {'Buy':<8} {'Sell':<8} {'Profit %':<8} {'Buy Price':<12} {'Sell Price':<12}")
        print("-" * 80)
        
        for opp in opportunities[:10]:
            time_str = opp['timestamp'][:19].replace('T', ' ')
            print(f"{time_str:<20} {opp['symbol']:<10} {opp['buy_exchange']:<8} {opp['sell_exchange']:<8} "
                  f"{opp['profit_pct']:<8.3f} ${opp['buy_price']:<11.2f} ${opp['sell_price']:<11.2f}")
        
        # Summary statistics
        print("\nSummary Statistics:")
        print("-" * 40)
        avg_profit = sum(opp['profit_pct'] for opp in opportunities) / len(opportunities)
        max_profit = max(opp['profit_pct'] for opp in opportunities)
        
        print(f"Average profit potential: {avg_profit:.3f}%")
        print(f"Maximum profit potential: {max_profit:.3f}%")
        
        # Count by symbol
        symbol_counts = {}
        for opp in opportunities:
            symbol = opp['symbol']
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        print(f"\nOpportunities by cryptocurrency:")
        for symbol, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {symbol}: {count} opportunities")
            
    else:
        print("No significant arbitrage opportunities detected.")
        print("This could be due to:")
        print("- Efficient markets with small spreads")
        print("- High trading fees reducing profitability")
        print("- Limited price data or exchange connectivity issues")

if __name__ == '__main__':
    analyze_price_data()
