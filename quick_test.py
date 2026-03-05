#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def test_binance():
    try:
        url = "https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        print(f"Binance BTC/USDT: Bid ${float(data['bidPrice']):.2f}, Ask ${float(data['askPrice']):.2f}")
        return True
    except Exception as e:
        print(f"Binance error: {e}")
        return False

def test_kraken():
    try:
        url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
        response = requests.get(url, timeout=5)
        data = response.json()
        if 'result' in data:
            pair_data = list(data['result'].values())[0]
            print(f"Kraken BTC/USD: Bid ${float(pair_data['b'][0]):.2f}, Ask ${float(pair_data['a'][0]):.2f}")
            return True
    except Exception as e:
        print(f"Kraken error: {e}")
        return False

def test_kucoin():
    try:
        url = "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data['code'] == '200000':
            ticker = data['data']
            print(f"KuCoin BTC/USDT: Bid ${float(ticker['bestBid']):.2f}, Ask ${float(ticker['bestAsk']):.2f}")
            return True
    except Exception as e:
        print(f"KuCoin error: {e}")
        return False

if __name__ == "__main__":
    print("Testing exchange APIs...")
    print("=" * 40)
    
    results = []
    results.append(("Binance", test_binance()))
    results.append(("Kraken", test_kraken()))
    results.append(("KuCoin", test_kucoin()))
    
    print("\nResults:")
    for exchange, success in results:
        status = "✅ Working" if success else "❌ Failed"
        print(f"{exchange}: {status}")
    
    working_exchanges = sum(1 for _, success in results if success)
    print(f"\nTotal working exchanges: {working_exchanges}/3")
