#!/usr/bin/env python3
"""
Focused crypto arbitrage monitor for Kraken and KuCoin
"""

import requests
import time
import json
from datetime import datetime

class FocusedArbitrageMonitor:
    def __init__(self):
        self.opportunities = []
        self.price_data = []
        
    def get_kraken_price(self, symbol):
        """Get price from Kraken public API"""
        try:
            # Symbol mapping for Kraken
            symbol_map = {
                'BTC/USDT': 'XBTUSD',
                'ETH/USDT': 'ETHUSD',
                'BNB/USDT': None,  # Not available on Kraken
                'ADA/USDT': 'ADAUSD',
                'SOL/USDT': 'SOLUSD'
            }
            
            kraken_symbol = symbol_map.get(symbol)
            if not kraken_symbol:
                return None
                
            url = f"https://api.kraken.com/0/public/Ticker?pair={kraken_symbol}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if 'result' in data and data['result']:
                pair_data = list(data['result'].values())[0]
                return {
                    'bid': float(pair_data['b'][0]),
                    'ask': float(pair_data['a'][0]),
                    'exchange': 'kraken',
                    'last': float(pair_data['c'][0])
                }
        except Exception as e:
            print(f"Kraken error for {symbol}: {e}")
            return None
    
    def get_kucoin_price(self, symbol):
        """Get price from KuCoin public API"""
        try:
            kucoin_symbol = symbol.replace('/', '-')
            url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={kucoin_symbol}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data['code'] == '200000':
                ticker_data = data['data']
                return {
                    'bid': float(ticker_data['bestBid']),
                    'ask': float(ticker_data['bestAsk']),
                    'exchange': 'kucoin',
                    'last': float(ticker_data['price'])
                }
        except Exception as e:
            print(f"KuCoin error for {symbol}: {e}")
            return None
    
    def analyze_arbitrage(self, symbol, kraken_price, kucoin_price):
        """Analyze arbitrage opportunity between two exchanges"""
        opportunities = []
        
        # Scenario 1: Buy on Kraken, sell on KuCoin
        if kraken_price['ask'] < kucoin_price['bid']:
            profit_pct = ((kucoin_price['bid'] - kraken_price['ask']) / kraken_price['ask']) * 100
            if profit_pct > 0.1:  # More than 0.1% profit
                opportunities.append({
                    'symbol': symbol,
                    'buy_exchange': 'kraken',
                    'sell_exchange': 'kucoin',
                    'buy_price': kraken_price['ask'],
                    'sell_price': kucoin_price['bid'],
                    'profit_percentage': profit_pct,
                    'profit_per_1000': profit_pct * 10,  # Profit per $1000 invested
                    'timestamp': datetime.now().isoformat()
                })
        
        # Scenario 2: Buy on KuCoin, sell on Kraken
        if kucoin_price['ask'] < kraken_price['bid']:
            profit_pct = ((kraken_price['bid'] - kucoin_price['ask']) / kucoin_price['ask']) * 100
            if profit_pct > 0.1:  # More than 0.1% profit
                opportunities.append({
                    'symbol': symbol,
                    'buy_exchange': 'kucoin',
                    'sell_exchange': 'kraken',
                    'buy_price': kucoin_price['ask'],
                    'sell_price': kraken_price['bid'],
                    'profit_percentage': profit_pct,
                    'profit_per_1000': profit_pct * 10,  # Profit per $1000 invested
                    'timestamp': datetime.now().isoformat()
                })
        
        return opportunities
    
    def scan_symbol(self, symbol):
        """Scan a symbol for arbitrage opportunities"""
        kraken_price = self.get_kraken_price(symbol)
        kucoin_price = self.get_kucoin_price(symbol)
        
        if not kraken_price or not kucoin_price:
            return 0
        
        # Show current prices
        print(f"  {symbol}:")
        print(f"    Kraken: ${kraken_price['last']:.2f} (Bid: ${kraken_price['bid']:.2f}, Ask: ${kraken_price['ask']:.2f})")
        print(f"    KuCoin: ${kucoin_price['last']:.2f} (Bid: ${kucoin_price['bid']:.2f}, Ask: ${kucoin_price['ask']:.2f})")
        
        # Analyze arbitrage opportunities
        opportunities = self.analyze_arbitrage(symbol, kraken_price, kucoin_price)
        
        for opp in opportunities:
            self.opportunities.append(opp)
            print(f"    💰 OPPORTUNITY: Buy on {opp['buy_exchange']} at ${opp['buy_price']:.4f}, "
                  f"sell on {opp['sell_exchange']} at ${opp['sell_price']:.4f} "
                  f"({opp['profit_percentage']:.3f}% profit, ${opp['profit_per_1000']:.2f} per $1000)")
        
        # Store price data
        price_entry = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'kraken': kraken_price,
            'kucoin': kucoin_price,
            'spread_pct': abs(kraken_price['last'] - kucoin_price['last']) / min(kraken_price['last'], kucoin_price['last']) * 100
        }
        self.price_data.append(price_entry)
        
        return len(opportunities)
    
    def run_monitoring(self, duration_minutes=55):
        """Run monitoring for specified duration"""
        print(f"🚀 Starting focused arbitrage monitoring (Kraken ↔ KuCoin)")
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print("=" * 70)
        
        # Focus on symbols available on both exchanges
        symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT']
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        scan_count = 0
        total_opportunities = 0
        
        while time.time() < end_time:
            scan_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            remaining_minutes = int((end_time - time.time()) / 60)
            
            print(f"\n🔍 Scan #{scan_count} at {current_time} ({remaining_minutes} min remaining)")
            print("-" * 50)
            
            scan_opportunities = 0
            for symbol in symbols:
                try:
                    opps = self.scan_symbol(symbol)
                    scan_opportunities += opps
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    print(f"  {symbol}: Error - {str(e)}")
            
            total_opportunities += scan_opportunities
            print(f"\n📊 Scan summary: {scan_opportunities} opportunities found")
            print(f"📈 Total opportunities so far: {len(self.opportunities)}")
            
            # Wait before next scan (every 20 seconds for more frequent monitoring)
            time.sleep(20)
        
        print(f"\n🏁 Monitoring completed!")
        print(f"📊 Final Statistics:")
        print(f"   • Total scans: {scan_count}")
        print(f"   • Total opportunities: {len(self.opportunities)}")
        print(f"   • Average opportunities per scan: {len(self.opportunities)/scan_count:.2f}")
        
        return scan_count

if __name__ == "__main__":
    monitor = FocusedArbitrageMonitor()
    scans = monitor.run_monitoring(10)  # Start with 10 minutes for testing
    
    print(f"\n🎯 BEST OPPORTUNITIES FOUND:")
    print("=" * 50)
    
    if monitor.opportunities:
        # Sort by profit percentage
        sorted_opps = sorted(monitor.opportunities, key=lambda x: x['profit_percentage'], reverse=True)
        
        for i, opp in enumerate(sorted_opps[:10]):  # Show top 10
            print(f"{i+1:2d}. {opp['symbol']} - {opp['profit_percentage']:.3f}% profit")
            print(f"     Buy: {opp['buy_exchange']} @ ${opp['buy_price']:.4f}")
            print(f"     Sell: {opp['sell_exchange']} @ ${opp['sell_price']:.4f}")
            print(f"     Profit per $1000: ${opp['profit_per_1000']:.2f}")
            print(f"     Time: {opp['timestamp'][:19]}")
            print()
        
        # Calculate statistics
        profits = [opp['profit_percentage'] for opp in monitor.opportunities]
        avg_profit = sum(profits) / len(profits)
        max_profit = max(profits)
        
        print(f"📈 Profit Statistics:")
        print(f"   • Average profit: {avg_profit:.3f}%")
        print(f"   • Maximum profit: {max_profit:.3f}%")
        print(f"   • Opportunities > 0.5%: {sum(1 for p in profits if p > 0.5)}")
        print(f"   • Opportunities > 1.0%: {sum(1 for p in profits if p > 1.0)}")
        
    else:
        print("No arbitrage opportunities found.")
        print("This could indicate:")
        print("• Efficient markets with tight spreads")
        print("• High trading fees reducing profitability")
        print("• Technical issues with data feeds")
    
    # Save results
    results = {
        'summary': {
            'total_scans': scans,
            'total_opportunities': len(monitor.opportunities),
            'monitoring_duration_minutes': 10,
            'exchanges': ['kraken', 'kucoin'],
            'symbols_monitored': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT']
        },
        'opportunities': monitor.opportunities,
        'price_data': monitor.price_data[-50:]  # Keep last 50 price entries
    }
    
    with open('arbitrage_monitoring_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to arbitrage_monitoring_results.json")
