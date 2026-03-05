"""
Verification script to confirm paper trading mode is active and no real trades will be executed
"""

import os
from dotenv import load_dotenv
from pathlib import Path

def verify_paper_trading_mode():
    """Verify that paper trading mode is properly configured"""
    
    print("\n" + "=" * 80)
    print("PAPER TRADING MODE VERIFICATION")
    print("=" * 80 + "\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check 1: Environment variable
    paper_mode = os.getenv('PAPER_TRADING_MODE', 'false').lower()
    print(f"1. Environment Variable Check:")
    print(f"   PAPER_TRADING_MODE = {paper_mode}")
    
    if paper_mode == 'true':
        print("   ✅ Paper trading mode is ENABLED")
        print("   ✅ No real trades will be executed\n")
    else:
        print("   ⚠️  WARNING: Paper trading mode is DISABLED")
        print("   ⚠️  Real trades WILL be executed if you run arbitrage_bot.py\n")
    
    # Check 2: File structure
    print(f"2. File Structure Check:")
    
    files_to_check = {
        'paper_trading_bot.py': 'Paper trading bot script',
        'demo_paper_trading.py': 'Demo paper trading script',
        'test_paper_trading.py': 'Test runner script',
        'PAPER_TRADING_GUIDE.md': 'Documentation',
        'paper_trading_logs/': 'Log directory'
    }
    
    all_present = True
    for file_path, description in files_to_check.items():
        exists = Path(file_path).exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {file_path: <30} - {description}")
        if not exists:
            all_present = False
    
    print()
    
    # Check 3: Log files
    log_dir = Path('paper_trading_logs')
    if log_dir.exists():
        log_files = list(log_dir.glob('*'))
        print(f"3. Generated Log Files:")
        print(f"   Found {len(log_files)} files in paper_trading_logs/")
        
        for log_file in sorted(log_files)[:5]:  # Show first 5
            size = log_file.stat().st_size
            print(f"   📄 {log_file.name} ({size:,} bytes)")
        
        if len(log_files) > 5:
            print(f"   ... and {len(log_files) - 5} more files")
    else:
        print(f"3. Log Directory:")
        print(f"   ⚠️  paper_trading_logs/ not found (will be created on first run)")
    
    print()
    
    # Check 4: Configuration
    try:
        from config import PAPER_TRADING_CONFIG, TRADING_CONFIG
        
        print(f"4. Configuration Settings:")
        print(f"   Paper Trading Enabled: {PAPER_TRADING_CONFIG.get('enabled', False)}")
        print(f"   Initial Virtual Balance: ${PAPER_TRADING_CONFIG.get('initial_balance', 0):.2f}")
        print(f"   Min Profit Threshold: {TRADING_CONFIG.get('min_profit_threshold', 0) * 100:.1f}%")
        print(f"   Max Trade Amount: ${TRADING_CONFIG.get('max_trade_amount', 0):.2f}")
        print(f"   Daily Limit: ${TRADING_CONFIG.get('daily_limit', 0):.2f}")
    except Exception as e:
        print(f"4. Configuration:")
        print(f"   ⚠️  Error loading config: {e}")
    
    print()
    
    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    if paper_mode == 'true' and all_present:
        print("\n✅ ✅ ✅  PAPER TRADING MODE IS ACTIVE  ✅ ✅ ✅\n")
        print("Safe to run:")
        print("  • python3 demo_paper_trading.py")
        print("  • python3 paper_trading_bot.py")
        print("  • python3 test_paper_trading.py")
        print("\nNo real trades will be executed!\n")
    elif paper_mode == 'true':
        print("\n⚠️  Paper trading mode enabled but some files are missing")
        print("Bot may not function correctly\n")
    else:
        print("\n🚨 🚨 🚨  WARNING: LIVE TRADING MODE  🚨 🚨 🚨\n")
        print("If you run arbitrage_bot.py, REAL TRADES will be executed!")
        print("\nTo enable paper trading mode:")
        print("  1. Edit .env file")
        print("  2. Set PAPER_TRADING_MODE=true")
        print("  3. Run this verification script again\n")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    verify_paper_trading_mode()
