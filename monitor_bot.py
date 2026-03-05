#!/usr/bin/env python3
"""
Bot monitoring script to track arbitrage opportunities and generate reports
"""

import sqlite3
import time
import json
from datetime import datetime, timedelta
import ccxt
from config import EXCHANGE_CONFIG, TRADING_CONFIG

def get_current_prices():
    """Get current prices from available exchanges"""
    prices = {}
    
    # Test Kraken
    try:
        kraken = ccxt.kraken(EXCHANGE_CONFIG['kraken'])
        kraken.load_markets()
        for symbol in TRADING_CONFIG['cryptocurrencies']:
            try:
                ticker = kraken.fetch_ticker(symbol)
                if symbol not in prices:
                    prices[symbol] = {}
                prices[symbol]['kraken'] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'timestamp': ticker['timestamp']
                }
            except:
                pass
    except:
        pass
    
    # Test KuCoin
    try:
        kucoin = ccxt.kucoin(EXCHANGE_CONFIG['kucoin'])
        kucoin.load_markets()
        for symbol in TRADING_CONFIG['cryptocurrencies']:
            try:
                ticker = kucoin.fetch_ticker(symbol)
                if symbol not in prices:
                    prices[symbol] = {}
                prices[symbol]['kucoin'] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'timestamp': ticker['timestamp']
                }
            except:
                pass
    except:
        pass
    
    return prices

def find_opportunities(prices):
    """Find arbitrage opportunities"""
    opportunities = []
    
    for symbol, exchange_prices in prices.items():
        if len(exchange_prices) < 2:
            continue
            
        exchanges = list(exchange_prices.keys())
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                buy_exchange = exchanges[i]
                sell_exchange = exchanges[j]
                
                buy_price = exchange_prices[buy_exchange]['ask']
                sell_price = exchange_prices[sell_exchange]['bid']
                
                if sell_price > buy_price:
                    profit_pct = ((sell_price - buy_price) / buy_price) * 100
                    if profit_pct > TRADING_CONFIG['min_profit_threshold'] * 100:
                        opportunities.append({
                            'symbol': symbol,
                            'buy_exchange': buy_exchange,
                            'sell_exchange': sell_exchange,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'profit_percentage': profit_pct,
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Check reverse direction
                buy_price = exchange_prices[sell_exchange]['ask']
                sell_price = exchange_prices[buy_exchange]['bid']
                
                if sell_price > buy_price:
                    profit_pct = ((sell_price - buy_price) / buy_price) * 100
                    if profit_pct > TRADING_CONFIG['min_profit_threshold'] * 100:
                        opportunities.append({
                            'symbol': symbol,
                            'buy_exchange': sell_exchange,
                            'sell_exchange': buy_exchange,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'profit_percentage': profit_pct,
                            'timestamp': datetime.now().isoformat()
                        })
    
    return opportunities

def monitor_and_log():
    """Monitor prices and log opportunities"""
    print(f"Starting monitoring at {datetime.now()}")
    
    while True:
        try:
            prices = get_current_prices()
            opportunities = find_opportunities(prices)
            
            timestamp = datetime.now().isoformat()
            
            # Log to file
            with open('monitoring_log.json', 'a') as f:
                log_entry = {
                    'timestamp': timestamp,
                    'prices': prices,
                    'opportunities': opportunities
                }
                f.write(json.dumps(log_entry) + '\n')
            
            if opportunities:
                print(f"[{timestamp}] Found {len(opportunities)} opportunities:")
                for opp in opportunities:
                    print(f"  {opp['symbol']}: {opp['buy_exchange']} -> {opp['sell_exchange']} "
                          f"({opp['profit_percentage']:.3f}%)")
            else:
                print(f"[{timestamp}] No opportunities found")
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == '__main__':
    monitor_and_log()
