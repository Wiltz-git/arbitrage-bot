"""
Test script for paper trading bot
Runs the bot for a specified duration to verify functionality
"""

import asyncio
import sys
from paper_trading_bot import PaperTradingBot


async def run_test(duration_minutes: int = 3):
    """
    Run paper trading bot for testing
    
    Args:
        duration_minutes: How long to run the test (default: 3 minutes)
    """
    print("\n" + "=" * 80)
    print("PAPER TRADING BOT - TEST MODE")
    print("=" * 80)
    print(f"\nThis test will run the paper trading bot for {duration_minutes} minutes.")
    print("The bot will:")
    print("  ✓ Scan for arbitrage opportunities every 5 seconds")
    print("  ✓ Log detailed information about each opportunity")
    print("  ✓ Simulate trades that meet the 1.5% profit threshold")
    print("  ✓ Track virtual portfolio balance")
    print("  ✗ NOT execute any real trades on exchanges")
    print("\nPress Ctrl+C at any time to stop early.\n")
    print("=" * 80 + "\n")
    
    # Create and start the bot
    bot = PaperTradingBot()
    
    try:
        await bot.start(duration_minutes=duration_minutes)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user...")
    except Exception as e:
        print(f"\n\nError during test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop the bot (this will generate the summary)
        if bot.is_running:
            bot.stop()
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        print(f"\nCheck the following files for results:")
        print(f"  • {bot.today_log_file}")
        print(f"  • paper_trading_logs/simulated_trades_*.json")
        print(f"  • paper_trading_logs/daily_summary_*.txt")
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    # Get duration from command line argument if provided
    duration = 3  # Default 3 minutes
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Usage: python test_paper_trading.py [duration_in_minutes]")
            sys.exit(1)
    
    asyncio.run(run_test(duration))
