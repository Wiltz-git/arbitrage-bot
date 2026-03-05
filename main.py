#!/usr/bin/env python3
"""
Crypto Arbitrage Bot - Main Entry Point
Automated cryptocurrency arbitrage trading across multiple exchanges
"""

import asyncio
import argparse
import sys
import os
from arbitrage_bot import ArbitrageBot
from dashboard import app, socketio
import threading

def run_bot_only():
    """Run only the arbitrage bot without dashboard"""
    print("Starting Crypto Arbitrage Bot...")
    
    bot = ArbitrageBot()
    
    try:
        # Send startup notification
        asyncio.run(bot.email_notifier.send_startup_notification())
        
        # Start the bot
        asyncio.run(bot.start())
        
    except KeyboardInterrupt:
        print("\nShutting down bot...")
        bot.stop()
        
        # Send shutdown notification
        asyncio.run(bot.email_notifier.send_shutdown_notification())
        
    except Exception as e:
        print(f"Error running bot: {e}")
        sys.exit(1)

def run_dashboard_only():
    """Run only the web dashboard"""
    print("Starting Crypto Arbitrage Bot Dashboard...")
    print("Dashboard will be available at http://localhost:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

def run_both():
    """Run both bot and dashboard"""
    print("Starting Crypto Arbitrage Bot with Dashboard...")
    print("Dashboard will be available at http://localhost:5000")
    
    # Start dashboard in main thread
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Crypto Arbitrage Bot')
    parser.add_argument('--mode', choices=['bot', 'dashboard', 'both'], 
                       default='both', help='Run mode (default: both)')
    parser.add_argument('--config-check', action='store_true',
                       help='Check configuration and exit')
    
    args = parser.parse_args()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("Please copy .env.example to .env and configure your API keys.")
        print("Example: cp .env.example .env")
        return
    
    # Configuration check
    if args.config_check:
        print("Checking configuration...")
        try:
            from config import EXCHANGE_CONFIG, EMAIL_CONFIG, TRADING_CONFIG
            
            print("✅ Configuration files loaded successfully")
            print(f"📊 Tracking {len(TRADING_CONFIG['cryptocurrencies'])} cryptocurrencies")
            print(f"🏦 Configured for {len(EXCHANGE_CONFIG)} exchanges")
            print(f"💰 Daily limit: ${TRADING_CONFIG['daily_limit']}")
            print(f"📧 Email notifications: {'Enabled' if EMAIL_CONFIG['email'] else 'Disabled'}")
            
            # Test exchange connections
            print("\nTesting exchange connections...")
            from exchange_manager import ExchangeManager
            em = ExchangeManager()
            status = em.get_exchange_status()
            
            for exchange, state in status.items():
                print(f"  {exchange}: {state}")
            
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return
        
        print("\n✅ Configuration check complete!")
        return
    
    # Run based on mode
    if args.mode == 'bot':
        run_bot_only()
    elif args.mode == 'dashboard':
        run_dashboard_only()
    else:
        run_both()

if __name__ == '__main__':
    main()