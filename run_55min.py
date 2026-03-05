#!/usr/bin/env python3
"""
Run paper trading bot for exactly 55 minutes
"""
import asyncio
import sys
from paper_trading_bot import PaperTradingBot

async def main():
    """Run bot for 55 minutes"""
    bot = PaperTradingBot()
    
    try:
        print("Starting 55-minute paper trading session...")
        await bot.start(duration_minutes=55)
        print("\n55-minute session complete!")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        bot.stop()
        print("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())
