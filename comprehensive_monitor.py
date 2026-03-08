#!/usr/bin/env python3
"""
Comprehensive monitoring script for crypto arbitrage bot
"""

import sqlite3
import time
import json
import os
from datetime import datetime, timedelta
import ccxt
from config import EXCHANGE_CONFIG, TRADING_CONFIG

class ArbitrageMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.opportunities_found = []
        self.price_history = []
        self.exchange_status = {}
        
    def test_exchange_connections(self):
        """Test which exchanges are working"""
        print("Testing exchange connections...")
        
        for exchange_name, config in EXCHANGE_CONFIG.items():
            try:
                if exchange_name == 'kraken':
                    exchange = ccxt.kraken(config)
                elif exchange_name == 'kucoin':
                    exchange = ccxt.kucoin(config)
                else:
                    continue  # Skip binance and coinbase as they're not working
                
                exchange.load_markets()
                # Test with BTC/USDT
                ticker = exchange.fetch_ticker('BTC/USDT')
                self.exchange_status[exchange_name] = 'connected'
                print(f"✅ {exchange_name}: Connected (BTC/USDT: ${ticker['last']:.2f})")
                
            except Exception as e:
                self.exchange_status[exchange_name] = f'error: {str(e)[:50]}'
                print(f"❌ {exchange_name}: {str(e)[:50]}")
    
    def get_current_prices(self):
        """Get current prices from working exchanges"""
        prices = {}
        timestamp = datetime.now()
        
        for exchange_name in ['kraken', 'kucoin']:
            if self.exchange_status.get(exchange_name) != 'connected':
                continue
                
            try:
                if exchange_name == 'kraken':
                    exchange = ccxt.kraken(EXCHANGE_CONFIG['kraken'])
                else:
                    exchange = ccxt.kucoin(EXCHANGE_CONFIG['kucoin'])
                
                exchange.load_markets()
                
                for symbol in TRADING_CONFIG['cryptocurrencies']:
                    try:
                        ticker = exchange.fetch_ticker(symbol)
                        if symbol not in prices:
                            prices[symbol] = {}
                        
                        prices[symbol][exchange_name] = {
                            'bid': ticker['bid'],
                            'ask': ticker['ask'],
                            'last': ticker['last'],
                            'timestamp': timestamp.isoformat()
                        }
                    except Exception as e:
                        print(f"Warning: Could not fetch {symbol} from {exchange_name}: {str(e)[:30]}")
                        
            except Exception as e:
                print(f"Error with {exchange_name}: {str(e)[:50]}")
        
        return prices
    
    def find_arbitrage_opportunities(self, prices):
        """Find arbitrage opportunities between exchanges"""
        opportunities = []
        
        for symbol, exchange_prices in prices.items():
            if len(exchange_prices) < 2:
                continue
            
            exchanges = list(exchange_prices.keys())
            
            for i in range(len(exchanges)):
                for j in range(i + 1, len(exchanges)):
                    buy_exchange = exchanges[i]
                    sell_exchange = exchanges[j]
                    
                    # Check opportunity: buy from i, sell to j
                    buy_price = exchange_prices[buy_exchange]['ask']  # Price to buy
                    sell_price = exchange_prices[sell_exchange]['bid']  # Price to sell
                    
                    if sell_price > buy_price:
                        profit_amount = sell_price - buy_price
                        profit_pct = (profit_amount / buy_price) * 100
                        
                        # Apply fee buffer
                        effective_profit_pct = profit_pct - (TRADING_CONFIG['fee_buffer'] * 100 * 2)  # 2x for buy and sell fees
                        
                        if effective_profit_pct > (TRADING_CONFIG['min_profit_threshold'] * 100):
                            opportunities.append({
                                'symbol': symbol,
                                'buy_exchange': buy_exchange,
                                'sell_exchange': sell_exchange,
                                'buy_price': buy_price,
                                'sell_price': sell_price,
                                'gross_profit_pct': profit_pct,
                                'net_profit_pct': effective_profit_pct,
                                'profit_amount': profit_amount,
                                'timestamp': datetime.now().isoformat()
                            })
                    
                    # Check reverse opportunity: buy from j, sell to i
                    buy_price = exchange_prices[sell_exchange]['ask']
                    sell_price = exchange_prices[buy_exchange]['bid']
                    
                    if sell_price > buy_price:
                        profit_amount = sell_price - buy_price
                        profit_pct = (profit_amount / buy_price) * 100
                        effective_profit_pct = profit_pct - (TRADING_CONFIG['fee_buffer'] * 100 * 2)
                        
                        if effective_profit_pct > (TRADING_CONFIG['min_profit_threshold'] * 100):
                            opportunities.append({
                                'symbol': symbol,
                                'buy_exchange': sell_exchange,
                                'sell_exchange': buy_exchange,
                                'buy_price': buy_price,
                                'sell_price': sell_price,
                                'gross_profit_pct': profit_pct,
                                'net_profit_pct': effective_profit_pct,
                                'profit_amount': profit_amount,
                                'timestamp': datetime.now().isoformat()
                            })
        
        return opportunities
    
    def monitor_session(self, duration_minutes=52):
        """Run monitoring session for specified duration"""
        print(f"Starting {duration_minutes}-minute monitoring session...")
        print(f"Start time: {self.start_time}")
        print(f"Minimum profit threshold: {TRADING_CONFIG['min_profit_threshold']*100:.1f}%")
        print("-" * 60)
        
        end_time = self.start_time + timedelta(minutes=duration_minutes)
        scan_count = 0
        
        while datetime.now() < end_time:
            try:
                scan_count += 1
                current_time = datetime.now()
                remaining = end_time - current_time
                
                print(f"\n[Scan #{scan_count}] {current_time.strftime('%H:%M:%S')} "
                      f"(Remaining: {remaining.seconds//60}m {remaining.seconds%60}s)")
                
                # Get current prices
                prices = self.get_current_prices()
                self.price_history.append({
                    'timestamp': current_time.isoformat(),
                    'prices': prices
                })
                
                # Find opportunities
                opportunities = self.find_arbitrage_opportunities(prices)
                
                if opportunities:
                    print(f"🎯 Found {len(opportunities)} arbitrage opportunities:")
                    for opp in opportunities:
                        print(f"   {opp['symbol']}: {opp['buy_exchange']} → {opp['sell_exchange']} "
                              f"({opp['net_profit_pct']:.3f}% net profit)")
                    
                    self.opportunities_found.extend(opportunities)
                else:
                    print("   No profitable opportunities found")
                
                # Show current prices
                for symbol, exchange_prices in prices.items():
                    if len(exchange_prices) >= 2:
                        price_info = []
                        for exchange, data in exchange_prices.items():
                            price_info.append(f"{exchange}: ${data['last']:.2f}")
                        print(f"   {symbol}: {' | '.join(price_info)}")
                
                time.sleep(30)  # Scan every 30 seconds
                
            except KeyboardInterrupt:
                print("\nMonitoring interrupted by user")
                break
            except Exception as e:
                print(f"Error during monitoring: {e}")
                time.sleep(10)
        
        print(f"\nMonitoring session completed at {datetime.now()}")
        return self.generate_report()
    
    def check_bot_database(self):
        """Check what the main bot has recorded in its database"""
        try:
            conn = sqlite3.connect('data/trades.db')
            cursor = conn.cursor()
            
            # Check opportunities
            cursor.execute("SELECT COUNT(*) FROM opportunities")
            opp_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM trades")
            trade_count = cursor.fetchone()[0]
            
            # Get recent opportunities
            cursor.execute("SELECT * FROM opportunities ORDER BY timestamp DESC LIMIT 10")
            recent_opps = cursor.fetchall()
            
            conn.close()
            
            return {
                'opportunities_count': opp_count,
                'trades_count': trade_count,
                'recent_opportunities': recent_opps
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_report(self):
        """Generate comprehensive trading report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Check bot database
        bot_data = self.check_bot_database()
        
        report = {
            'session_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': duration.total_seconds() / 60,
                'scans_performed': len(self.price_history)
            },
            'exchange_status': self.exchange_status,
            'opportunities_found': len(self.opportunities_found),
            'unique_opportunities': len(set((opp['symbol'], opp['buy_exchange'], opp['sell_exchange']) 
                                          for opp in self.opportunities_found)),
            'bot_database': bot_data,
            'best_opportunities': sorted(self.opportunities_found, 
                                       key=lambda x: x['net_profit_pct'], reverse=True)[:10],
            'summary_stats': self.calculate_summary_stats()
        }
        
        return report
    
    def calculate_summary_stats(self):
        """Calculate summary statistics"""
        if not self.opportunities_found:
            return {'message': 'No opportunities found during monitoring period'}
        
        profits = [opp['net_profit_pct'] for opp in self.opportunities_found]
        symbols = [opp['symbol'] for opp in self.opportunities_found]
        
        return {
            'total_opportunities': len(self.opportunities_found),
            'avg_profit_pct': sum(profits) / len(profits),
            'max_profit_pct': max(profits),
            'min_profit_pct': min(profits),
            'most_common_symbol': max(set(symbols), key=symbols.count),
            'symbols_with_opportunities': list(set(symbols))
        }

if __name__ == '__main__':
    monitor = ArbitrageMonitor()
    monitor.test_exchange_connections()
    report = monitor.monitor_session(52)  # 52 minutes remaining
    
    # Save report
    with open('monitoring_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to monitoring_report.json")
