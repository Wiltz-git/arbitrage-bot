#!/usr/bin/env python3
"""
Coinbase Ed25519 Diagnostic Script
Tests connection to Coinbase Advanced Trade API with Ed25519 credentials
"""

import ccxt
import sys
import traceback
from datetime import datetime

# Test credentials (Ed25519)
API_KEY = "5c17c730-ff94-4289-8b62-ed2f44503846"
SECRET = "iTQvrf1YHFUDSdQtXtSgJtrLMttJbI8iFs/+PL0Qhs6ZICeFkJ4BUpzJt6edzBiXSgrfMSWyXdzdJNltfNSPmw=="

def print_separator():
    print("\n" + "="*80 + "\n")

def test_coinbase_connection(config_name, exchange_config):
    """Test connection to Coinbase with given configuration"""
    print(f"Testing {config_name}...")
    print(f"Configuration: {exchange_config}")
    
    try:
        # Create exchange instance
        exchange = ccxt.coinbase(exchange_config)
        
        # Test 1: Load markets
        print("\n  [1/4] Loading markets...")
        markets = exchange.load_markets()
        print(f"  ✓ Successfully loaded {len(markets)} markets")
        
        # Test 2: Fetch ticker
        print("\n  [2/4] Fetching BTC/USDT ticker...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"  ✓ BTC/USDT Price: ${ticker['last']:,.2f}")
        print(f"      Bid: ${ticker['bid']:,.2f}, Ask: ${ticker['ask']:,.2f}")
        
        # Test 3: Fetch balance (requires authentication)
        print("\n  [3/4] Fetching account balance...")
        balance = exchange.fetch_balance()
        print(f"  ✓ Successfully authenticated and fetched balance")
        print(f"      Free USDT: ${balance.get('USDT', {}).get('free', 0):,.2f}")
        print(f"      Total assets: {len([k for k, v in balance.items() if isinstance(v, dict) and v.get('total', 0) > 0])}")
        
        # Test 4: Check account info
        print("\n  [4/4] Fetching accounts...")
        accounts = exchange.fetch_accounts()
        print(f"  ✓ Found {len(accounts)} accounts")
        
        print(f"\n✅ ALL TESTS PASSED for {config_name}")
        return True
        
    except ccxt.AuthenticationError as e:
        print(f"\n❌ AUTHENTICATION ERROR for {config_name}")
        print(f"   Error: {str(e)}")
        print(f"   This typically means:")
        print(f"   - API key or secret is incorrect")
        print(f"   - Key format is not supported by this CCXT version")
        print(f"   - Ed25519 signature not supported (requires CCXT >= 4.5.4)")
        return False
        
    except ccxt.NetworkError as e:
        print(f"\n❌ NETWORK ERROR for {config_name}")
        print(f"   Error: {str(e)}")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR for {config_name}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        traceback.print_exc()
        return False

def main():
    print("COINBASE ED25519 DIAGNOSTIC SCRIPT")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # Show CCXT version
    print(f"CCXT Version: {ccxt.__version__}")
    print(f"Python Version: {sys.version}")
    
    # Check if Ed25519 is supported
    if hasattr(ccxt, '__version__'):
        major, minor, patch = map(int, ccxt.__version__.split('.'))
        ed25519_supported = (major > 4) or (major == 4 and minor > 5) or (major == 4 and minor == 5 and patch >= 4)
        
        if ed25519_supported:
            print("✓ Ed25519 support: AVAILABLE (CCXT >= 4.5.4)")
        else:
            print("⚠ Ed25519 support: NOT AVAILABLE (requires CCXT >= 4.5.4)")
            print(f"  Current version: {ccxt.__version__}")
            print(f"  Required version: >= 4.5.4")
            print("\n  RECOMMENDATION: Upgrade CCXT with:")
            print("  pip install --upgrade ccxt")
    
    print_separator()
    
    # Test Configuration 1: Basic configuration (as in current code)
    config_basic = {
        'api_key': API_KEY,
        'secret': SECRET,
        'enableRateLimit': True,
    }
    result_basic = test_coinbase_connection("Basic Configuration", config_basic)
    
    print_separator()
    
    # Test Configuration 2: With verbose mode for debugging
    config_verbose = {
        'api_key': API_KEY,
        'secret': SECRET,
        'enableRateLimit': True,
        'verbose': False,  # Set to True for detailed debugging
    }
    result_verbose = test_coinbase_connection("Configuration with Verbose", config_verbose)
    
    print_separator()
    
    # Test Configuration 3: With explicit timeout
    config_timeout = {
        'api_key': API_KEY,
        'secret': SECRET,
        'enableRateLimit': True,
        'timeout': 30000,  # 30 seconds
    }
    result_timeout = test_coinbase_connection("Configuration with Timeout", config_timeout)
    
    print_separator()
    
    # Summary
    print("DIAGNOSTIC SUMMARY")
    print(f"CCXT Version: {ccxt.__version__}")
    print(f"Basic Configuration: {'✅ PASSED' if result_basic else '❌ FAILED'}")
    print(f"Verbose Configuration: {'✅ PASSED' if result_verbose else '❌ FAILED'}")
    print(f"Timeout Configuration: {'✅ PASSED' if result_timeout else '❌ FAILED'}")
    
    if not any([result_basic, result_verbose, result_timeout]):
        print("\n⚠️  ALL TESTS FAILED - RECOMMENDATIONS:")
        print("1. Upgrade CCXT to version >= 4.5.4 for Ed25519 support")
        print("   Command: pip install --upgrade ccxt")
        print("2. Verify your API key and secret are correct")
        print("3. Ensure your API key has proper permissions on Coinbase")
        print("4. Check that your API key is for Coinbase Advanced Trade (not legacy)")
    
    print_separator()

if __name__ == "__main__":
    main()
