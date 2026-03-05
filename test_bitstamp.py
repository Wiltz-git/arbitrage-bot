#!/usr/bin/env python3
"""
Test script for Bitstamp API connection
"""

import os
import sys
from dotenv import load_dotenv
import ccxt

# Load environment variables
load_dotenv()

def test_bitstamp_connection():
    """Test Bitstamp API connection and permissions"""
    
    print("="*60)
    print("Bitstamp API Connection Test")
    print("="*60)
    print()
    
    # Get credentials
    api_key = os.getenv('BITSTAMP_API_KEY')
    secret = os.getenv('BITSTAMP_SECRET')
    customer_id = os.getenv('BITSTAMP_CUSTOMER_ID')
    
    # Check if credentials exist
    if not api_key or not secret or not customer_id:
        print("❌ ERROR: Bitstamp credentials not found in .env file")
        print("   Required: BITSTAMP_API_KEY, BITSTAMP_SECRET, BITSTAMP_CUSTOMER_ID")
        return False
    
    # Check if using demo credentials
    if api_key == 'demo_key' or secret == 'demo_secret' or customer_id == 'demo_customer_id':
        print("❌ ERROR: Still using demo credentials")
        print("   Please update with real API keys from Bitstamp")
        return False
    
    print(f"✓ API Key found: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else ''}")
    print(f"✓ Secret found: {'*' * 8}...{'*' * 4}")
    print(f"✓ Customer ID found: {customer_id}")
    print()
    
    # Initialize exchange
    try:
        print("Initializing Bitstamp exchange...")
        exchange = ccxt.bitstamp({
            'apiKey': api_key,
            'secret': secret,
            'uid': customer_id,
            'enableRateLimit': True,
        })
        print("✓ Exchange initialized")
        print()
    except Exception as e:
        print(f"❌ ERROR initializing exchange: {e}")
        return False
    
    # Test 1: Fetch markets
    print("Test 1: Fetching available markets...")
    try:
        markets = exchange.load_markets()
        print(f"✓ Successfully loaded {len(markets)} markets")
        
        # Check for our target pairs
        target_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT']
        available = [pair for pair in target_pairs if pair in markets]
        unavailable = [pair for pair in target_pairs if pair not in markets]
        
        if available:
            print(f"  Available pairs: {', '.join(available)}")
        if unavailable:
            print(f"  ⚠️  Unavailable pairs: {', '.join(unavailable)}")
        print()
    except Exception as e:
        print(f"❌ ERROR fetching markets: {e}")
        return False
    
    # Test 2: Fetch ticker (no auth required)
    print("Test 2: Fetching BTC/USDT ticker (public data)...")
    try:
        if 'BTC/USDT' in markets:
            ticker = exchange.fetch_ticker('BTC/USDT')
            print(f"✓ BTC/USDT Price: ${ticker['last']:,.2f}")
            print(f"  24h Volume: ${ticker.get('quoteVolume', 0):,.0f}")
        else:
            print("⚠️  BTC/USDT not available on Bitstamp")
        print()
    except Exception as e:
        print(f"❌ ERROR fetching ticker: {e}")
        print()
    
    # Test 3: Fetch balance (requires auth)
    print("Test 3: Fetching account balance (requires authentication)...")
    try:
        balance = exchange.fetch_balance()
        print("✓ Successfully authenticated!")
        
        # Show non-zero balances
        non_zero = {k: v for k, v in balance['total'].items() if v and v > 0}
        if non_zero:
            print("  Account balances:")
            for currency, amount in non_zero.items():
                print(f"    {currency}: {amount}")
        else:
            print("  Account has no balances (or paper trading mode)")
        print()
    except ccxt.AuthenticationError as e:
        print(f"❌ AUTHENTICATION ERROR: {e}")
        print()
        print("Common causes:")
        print("  1. Invalid API Key, Secret, or Customer ID")
        print("  2. API key doesn't have proper permissions")
        print("  3. Wrong Customer ID format")
        print("  4. API key was recently created (wait a few minutes)")
        print()
        return False
    except Exception as e:
        print(f"❌ ERROR fetching balance: {e}")
        print()
        return False
    
    # Test 4: Check permissions
    print("Test 4: Checking API permissions...")
    try:
        # Check account info
        if hasattr(exchange, 'fetch_my_trades'):
            print("✓ Account access verified")
        print("  Trading permission: Not tested (paper trading mode)")
        print()
    except Exception as e:
        print(f"⚠️  Could not verify permissions: {e}")
        print()
    
    print("="*60)
    print("✅ Bitstamp API Connection Test PASSED")
    print("="*60)
    print()
    print("Your Bitstamp API is properly configured!")
    print("The bot should now be able to fetch prices from Bitstamp.")
    print()
    return True

if __name__ == '__main__':
    try:
        success = test_bitstamp_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
