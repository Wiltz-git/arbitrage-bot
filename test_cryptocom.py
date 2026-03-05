#!/usr/bin/env python3
"""
Test script for Crypto.com API connection
"""

import os
import sys
from dotenv import load_dotenv
import ccxt

# Load environment variables
load_dotenv()

def test_cryptocom_connection():
    """Test Crypto.com API connection and permissions"""
    
    print("="*60)
    print("Crypto.com API Connection Test")
    print("="*60)
    print()
    
    # Get credentials
    api_key = os.getenv('CRYPTOCOM_API_KEY')
    secret = os.getenv('CRYPTOCOM_SECRET')
    
    # Check if credentials exist
    if not api_key or not secret:
        print("❌ ERROR: Crypto.com credentials not found in .env file")
        print("   Please run update_cryptocom_credentials.sh first")
        return False
    
    # Check if using demo credentials
    if api_key == 'demo_key' or secret == 'demo_secret':
        print("❌ ERROR: Still using demo credentials")
        print("   Please update with real API keys from Crypto.com Exchange")
        return False
    
    print(f"✓ API Key found: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else ''}")
    print(f"✓ Secret found: {'*' * 8}...{'*' * 4}")
    print()
    
    # Initialize exchange
    try:
        print("Initializing Crypto.com exchange...")
        exchange = ccxt.cryptocom({
            'apiKey': api_key,
            'secret': secret,
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
            print(f"  24h Volume: ${ticker['quoteVolume']:,.0f}")
        else:
            print("⚠️  BTC/USDT not available on Crypto.com")
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
        print("  1. Invalid API Key or Secret")
        print("  2. API key doesn't have READ permission enabled")
        print("  3. IP whitelist restriction (if enabled)")
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
        # Try to fetch order history (requires auth)
        orders = exchange.fetch_orders(symbol='BTC/USDT', limit=1)
        print("✓ READ permission: Enabled")
        
        # Note: We won't test TRADE permission in paper trading mode
        print("  TRADE permission: Not tested (paper trading mode)")
        print()
    except ccxt.AuthenticationError:
        print("⚠️  Could not verify order history access")
        print("   This is okay for basic price fetching")
        print()
    except Exception as e:
        print(f"⚠️  Could not check permissions: {e}")
        print()
    
    print("="*60)
    print("✅ Crypto.com API Connection Test PASSED")
    print("="*60)
    print()
    print("Your Crypto.com API is properly configured!")
    print("The bot should now be able to fetch prices from Crypto.com.")
    print()
    return True

if __name__ == '__main__':
    try:
        success = test_cryptocom_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
