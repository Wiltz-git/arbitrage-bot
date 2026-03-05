import ccxt
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from config import EXCHANGE_CONFIG, TRADING_CONFIG

class ExchangeManager:
    """Manages connections and operations across multiple cryptocurrency exchanges"""
    
    def __init__(self):
        self.exchanges = {}
        self.logger = logging.getLogger(__name__)
        self.initialize_exchanges()
    
    def initialize_exchanges(self):
        """Initialize connections to all configured exchanges"""
        for exchange_name, config in EXCHANGE_CONFIG.items():
            try:
                if exchange_name == 'kraken':
                    self.exchanges[exchange_name] = ccxt.kraken(config)
                elif exchange_name == 'coinbase':
                    self.exchanges[exchange_name] = ccxt.coinbase(config)
                elif exchange_name == 'bitstamp':
                    self.exchanges[exchange_name] = ccxt.bitstamp(config)
                elif exchange_name == 'cryptocom':
                    self.exchanges[exchange_name] = ccxt.cryptocom(config)
                
                # Test connection
                self.exchanges[exchange_name].load_markets()
                self.logger.info(f"Successfully connected to {exchange_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to connect to {exchange_name}: {str(e)}")
                if exchange_name in self.exchanges:
                    del self.exchanges[exchange_name]
    
    async def get_ticker_prices(self, symbol: str) -> Dict[str, float]:
        """Get current ticker prices from all exchanges for a given symbol"""
        prices = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                ticker = await self._fetch_ticker_async(exchange, symbol)
                if ticker and 'bid' in ticker and 'ask' in ticker:
                    prices[exchange_name] = {
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'timestamp': ticker['timestamp']
                    }
            except Exception as e:
                self.logger.warning(f"Failed to get {symbol} price from {exchange_name}: {str(e)}")
        
        return prices
    
    async def _fetch_ticker_async(self, exchange, symbol):
        """Async wrapper for fetching ticker data"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, exchange.fetch_ticker, symbol)
    
    def find_arbitrage_opportunities(self, prices: Dict[str, Dict]) -> List[Dict]:
        """Identify arbitrage opportunities from price data"""
        opportunities = []
        
        if len(prices) < 2:
            return opportunities
        
        exchanges = list(prices.keys())
        
        # Compare all exchange pairs
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                exchange_a = exchanges[i]
                exchange_b = exchanges[j]
                
                price_a = prices[exchange_a]
                price_b = prices[exchange_b]
                
                # Check if we can buy on A and sell on B
                profit_a_to_b = self._calculate_profit(
                    price_a['ask'], price_b['bid'], exchange_a, exchange_b
                )
                
                # Check if we can buy on B and sell on A
                profit_b_to_a = self._calculate_profit(
                    price_b['ask'], price_a['bid'], exchange_b, exchange_a
                )
                
                # Add profitable opportunities
                if profit_a_to_b['profit_percentage'] >= TRADING_CONFIG['min_profit_threshold']:
                    opportunities.append({
                        'buy_exchange': exchange_a,
                        'sell_exchange': exchange_b,
                        'buy_price': price_a['ask'],
                        'sell_price': price_b['bid'],
                        'profit_percentage': profit_a_to_b['profit_percentage'],
                        'profit_amount': profit_a_to_b['profit_amount'],
                        'recommended_amount': profit_a_to_b['recommended_amount']
                    })
                
                if profit_b_to_a['profit_percentage'] >= TRADING_CONFIG['min_profit_threshold']:
                    opportunities.append({
                        'buy_exchange': exchange_b,
                        'sell_exchange': exchange_a,
                        'buy_price': price_b['ask'],
                        'sell_price': price_a['bid'],
                        'profit_percentage': profit_b_to_a['profit_percentage'],
                        'profit_amount': profit_b_to_a['profit_amount'],
                        'recommended_amount': profit_b_to_a['recommended_amount']
                    })
        
        return sorted(opportunities, key=lambda x: x['profit_percentage'], reverse=True)
    
    def _calculate_profit(self, buy_price: float, sell_price: float, 
                         buy_exchange: str, sell_exchange: str) -> Dict:
        """Calculate profit for an arbitrage opportunity"""
        # Account for fees (approximate 0.1% per exchange)
        total_fees = 0.002  # 0.2% total fees
        fee_buffer = TRADING_CONFIG['fee_buffer']
        
        # Calculate net profit percentage
        gross_profit = (sell_price - buy_price) / buy_price
        net_profit = gross_profit - total_fees - fee_buffer
        
        # Calculate recommended trade amount
        max_amount = min(TRADING_CONFIG['max_trade_amount'], 
                        self._get_available_balance(buy_exchange))
        
        profit_amount = max_amount * net_profit
        
        return {
            'profit_percentage': net_profit,
            'profit_amount': profit_amount,
            'recommended_amount': max_amount
        }
    
    def _get_available_balance(self, exchange_name: str) -> float:
        """Get available USDT balance for trading"""
        try:
            exchange = self.exchanges[exchange_name]
            balance = exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            
            # Apply reserve percentage
            available = usdt_balance * (1 - TRADING_CONFIG['reserve_percentage'])
            return min(available, TRADING_CONFIG['max_trade_amount'])
            
        except Exception as e:
            self.logger.error(f"Failed to get balance from {exchange_name}: {str(e)}")
            return 0
    
    async def execute_arbitrage_trade(self, opportunity: Dict, symbol: str) -> Dict:
        """Execute an arbitrage trade"""
        try:
            buy_exchange = self.exchanges[opportunity['buy_exchange']]
            sell_exchange = self.exchanges[opportunity['sell_exchange']]
            
            amount = opportunity['recommended_amount']
            
            # Execute buy order
            buy_order = await self._place_order_async(
                buy_exchange, symbol, 'market', 'buy', amount
            )
            
            if not buy_order or buy_order['status'] != 'closed':
                raise Exception("Buy order failed")
            
            # Execute sell order
            sell_order = await self._place_order_async(
                sell_exchange, symbol, 'market', 'sell', amount
            )
            
            if not sell_order or sell_order['status'] != 'closed':
                raise Exception("Sell order failed")
            
            # Calculate actual profit
            actual_profit = (sell_order['average'] - buy_order['average']) * amount
            
            return {
                'success': True,
                'buy_order': buy_order,
                'sell_order': sell_order,
                'profit': actual_profit,
                'amount': amount
            }
            
        except Exception as e:
            self.logger.error(f"Trade execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _place_order_async(self, exchange, symbol, order_type, side, amount):
        """Async wrapper for placing orders"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, exchange.create_order, symbol, order_type, side, amount
        )
    
    def get_exchange_status(self) -> Dict:
        """Get status of all exchanges"""
        status = {}
        for name, exchange in self.exchanges.items():
            try:
                # Test connection
                exchange.fetch_ticker('BTC/USDT')
                status[name] = 'connected'
            except:
                status[name] = 'disconnected'
        
        return status