#!/usr/bin/env python3
"""
Simple crypto arbitrage monitor using public APIs
"""

import requests
import time
import json
from datetime import datetime
import sqlite3

class SimpleArbitrageMonitor:
    def __init__(self):
        self.opportunities = []
        self.price_data = []
        
    def get_binance_price(self, symbol):
        """Get price from Binance public API"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={symbol.replace('/', '')}"
            response = requests.get(url, timeout=10)
            data = response.json()
            return {
                'bid': float(data['bidPrice']),
                'ask': float(data['askPrice']),
                'exchange': 'binance'
            }
        except:
            return None
    
    def get_kraken_price(self, symbol):
        """Get price from Kraken public API"""
        try:
            # Convert symbol format for Kraken
            kraken_symbol = symbol.replace('/', '').replace('USDT', 'USD')
            url = f"https://api.kraken.com/0/public/Ticker?pair={kraken_symbol}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'result' in data and data['result']:
                pair_data = list(data['result'].values())[0]
                return {
                    'bid': float(pair_data['b'][0]),
                    'ask': float(pair_data['a'][0]),
                    'exchange': 'kraken'
                }
        except:
            return None
    
    def get_kucoin_price(self, symbol):
        """Get price from KuCoin public API"""
        try:
            kucoin_symbol = symbol.replace('/', '-')
            url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={kucoin_symbol}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['code'] == '200000':
                ticker_data = data['data']
                return {
                    'bid': float(ticker_data['bestBid']),
                    'ask': float(ticker_data['bestAsk']),
                    'exchange': 'kucoin'
                }
        except:
            return None
    
    def get_coinbase_price(self, symbol):
        """Get price from Coinbase public API"""
        try:
            coinbase_symbol = symbol.replace('/', '-')
            url = f"https://api.exchange.coinbase.com/products/{coinbase_symbol}/ticker"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            return {
                'bid': float(data['bid']),
                'ask': float(data['ask']),
                'exchange': 'coinbase'
            }
        except:
            return None
    
    def scan_symbol(self, symbol):
        """Scan a symbol across exchanges"""
        print(f"Scanning {symbol}...")
        
        prices = []
        
        # Get prices from different exchanges
        binance_price = self.get_binance_price(symbol)
        if binance_price:
            prices.append(binance_price)
            
        kraken_price = self.get_kraken_price(symbol)
        if kraken_price:
            prices.append(kraken_price)
            
        kucoin_price = self.get_kucoin_price(symbol)
        if kucoin_price:
            prices.append(kucoin_price)
            
        coinbase_price = self.get_coinbase_price(symbol)
        if coinbase_price:
            prices.append(coinbase_price)
        
        if len(prices) >= 2:
            # Find arbitrage opportunities
            for i in range(len(prices)):
                for j in range(i + 1, len(prices)):
                    price1, price2 = prices[i], prices[j]
                    
                    # Calculate potential profit (buy low, sell high)
                    if price1['ask'] < price2['bid']:
                        profit_pct = ((price2['bid'] - price1['ask']) / price1['ask']) * 100
                        if profit_pct > 0.5:  # More than 0.5% profit
                            opportunity = {
                                'symbol': symbol,
                                'buy_exchange': price1['exchange'],
                                'sell_exchange': price2['exchange'],
                                'buy_price': price1['ask'],
                                'sell_price': price2['bid'],
                                'profit_percentage': profit_pct,
                                'timestamp': datetime.now().isoformat()
                            }
                            self.opportunities.append(opportunity)
                            print(f"  💰 Opportunity: Buy {symbol} on {price1['exchange']} at ${price1['ask']:.4f}, "
                                  f"sell on {price2['exchange']} at ${price2['bid']:.4f} "
                                  f"({profit_pct:.2f}% profit)")
                    
                    elif price2['ask'] < price1['bid']:
                        profit_pct = ((price1['bid'] - price2['ask']) / price2['ask']) * 100
                        if profit_pct > 0.5:  # More than 0.5% profit
                            opportunity = {
                                'symbol': symbol,
                                'buy_exchange': price2['exchange'],
                                'sell_exchange': price1['exchange'],
                                'buy_price': price2['ask'],
                                'sell_price': price1['bid'],
                                'profit_percentage': profit_pct,
                                'timestamp': datetime.now().isoformat()
                            }
                            self.opportunities.append(opportunity)
                            print(f"  💰 Opportunity: Buy {symbol} on {price2['exchange']} at ${price2['ask']:.4f}, "
                                  f"sell on {price1['exchange']} at ${price1['bid']:.4f} "
                                  f"({profit_pct:.2f}% profit)")
        
        # Store price data
        price_entry = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'prices': {p['exchange']: {'bid': p['bid'], 'ask': p['ask']} for p in prices}
        }
        self.price_data.append(price_entry)
        
        return len(prices)
    
    def run_monitoring(self, duration_minutes=55):
        """Run monitoring for specified duration"""
        print(f"Starting crypto arbitrage monitoring for {duration_minutes} minutes...")
        print("=" * 60)
        
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT']
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        scan_count = 0
        
        while time.time() < end_time:
            scan_count += 1
            print(f"\n--- Scan #{scan_count} at {datetime.now().strftime('%H:%M:%S')} ---")
            
            for symbol in symbols:
                try:
                    exchanges_found = self.scan_symbol(symbol)
                    print(f"  {symbol}: Found prices from {exchanges_found} exchanges")
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"  {symbol}: Error - {str(e)}")
            
            print(f"Total opportunities found so far: {len(self.opportunities)}")
            
            # Wait before next scan (every 30 seconds)
            time.sleep(30)
        
        print(f"\n🏁 Monitoring completed after {scan_count} scans")
        return scan_count

if __name__ == "__main__":
    monitor = SimpleArbitrageMonitor()
    scans = monitor.run_monitoring(55)
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"Total scans: {scans}")
    print(f"Total opportunities found: {len(monitor.opportunities)}")
    
    if monitor.opportunities:
        print("\n🎯 Best opportunities:")
        sorted_opps = sorted(monitor.opportunities, key=lambda x: x['profit_percentage'], reverse=True)
        for i, opp in enumerate(sorted_opps[:5]):
            print(f"{i+1}. {opp['symbol']}: {opp['profit_percentage']:.2f}% profit "
                  f"({opp['buy_exchange']} → {opp['sell_exchange']})")
    
    # Save results
    with open('monitoring_results.json', 'w') as f:
        json.dump({
            'opportunities': monitor.opportunities,
            'price_data': monitor.price_data,
            'summary': {
                'total_scans': scans,
                'total_opportunities': len(monitor.opportunities),
                'monitoring_duration': 55
            }
        }, f, indent=2)
    
    print(f"\n💾 Results saved to monitoring_results.json")
