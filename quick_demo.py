#!/usr/bin/env python3
"""
Quick Demo Arbitrage Results Generator
"""

import json
import random
from datetime import datetime, timedelta

def generate_demo_results():
    """Generate demo arbitrage results"""
    
    # Base prices for cryptocurrencies
    base_prices = {
        'BTC/USDT': 109000,
        'ETH/USDT': 4530,
        'BNB/USDT': 854,
        'ADA/USDT': 1.45,
        'SOL/USDT': 245,
        'DOT/USDT': 12.5
    }
    
    exchanges = ['kraken', 'kucoin', 'binance', 'coinbase']
    
    # Generate some sample trades
    trades = []
    total_profit = 0
    
    for i in range(15):  # Generate 15 sample trades
        symbol = random.choice(list(base_prices.keys()))
        buy_exchange = random.choice(exchanges)
        sell_exchange = random.choice([e for e in exchanges if e != buy_exchange])
        
        base_price = base_prices[symbol]
        buy_price = base_price * random.uniform(0.998, 1.002)
        sell_price = buy_price * random.uniform(1.016, 1.035)  # 1.6-3.5% profit
        
        profit_pct = ((sell_price - buy_price) / buy_price) * 100
        profit_usd = profit_pct * 10  # $1000 trade amount
        total_profit += profit_usd
        
        trade = {
            'id': i + 1,
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 55))).isoformat(),
            'symbol': symbol,
            'buy_exchange': buy_exchange,
            'sell_exchange': sell_exchange,
            'buy_price': round(buy_price, 2 if base_price > 100 else 4),
            'sell_price': round(sell_price, 2 if base_price > 100 else 4),
            'amount_usd': 1000,
            'profit_usd': round(profit_usd, 2),
            'profit_pct': round(profit_pct, 2),
            'status': 'executed'
        }
        trades.append(trade)
    
    # Generate price samples
    price_samples = []
    for symbol in base_prices.keys():
        base_price = base_prices[symbol]
        prices = {}
        for exchange in exchanges:
            variation = random.uniform(-0.005, 0.005)
            price = base_price * (1 + variation)
            spread = random.uniform(0.0001, 0.0005)
            
            prices[exchange] = {
                'bid': round(price * (1 - spread/2), 2 if base_price > 100 else 4),
                'ask': round(price * (1 + spread/2), 2 if base_price > 100 else 4)
            }
        
        price_samples.append({
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'prices': prices
        })
    
    # Create comprehensive report
    report = {
        'session_info': {
            'start_time': (datetime.now() - timedelta(minutes=55)).isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_minutes': 55,
            'total_scans': 110,  # Every 30 seconds for 55 minutes
            'symbols_monitored': list(base_prices.keys()),
            'exchanges_monitored': exchanges,
            'trades_executed': len(trades),
            'total_profit_usd': round(total_profit, 2),
            'average_profit_per_trade': round(total_profit / len(trades), 2),
            'demo_mode': True
        },
        'trades': sorted(trades, key=lambda x: x['timestamp']),
        'price_samples': price_samples,
        'summary_stats': {
            'most_profitable_pair': ['BTC/USDT', round(sum(t['profit_usd'] for t in trades if t['symbol'] == 'BTC/USDT'), 2)],
            'best_exchange_combination': ['binance -> kraken', round(sum(t['profit_usd'] for t in trades if t['buy_exchange'] == 'binance' and t['sell_exchange'] == 'kraken'), 2)],
            'hourly_profit_rate': round(total_profit * (60/55), 2)
        }
    }
    
    return report

if __name__ == "__main__":
    print("Generating demo arbitrage results...")
    report = generate_demo_results()
    
    # Save to file
    with open('demo_arbitrage_results.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Demo results generated!")
    print(f"📊 Trades executed: {report['session_info']['trades_executed']}")
    print(f"💰 Total profit: ${report['session_info']['total_profit_usd']}")
    print(f"📈 Average profit per trade: ${report['session_info']['average_profit_per_trade']}")
    print(f"📁 Results saved to: demo_arbitrage_results.json")
