#!/usr/bin/env python3
"""
Efficient monitoring - check status periodically and generate report when done
"""

import time
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

# Bot started at approximately 14:51, should end at 15:46 (55 minutes later)
START_TIME = datetime(2026, 1, 27, 14, 51, 0)
END_TIME = datetime(2026, 1, 27, 15, 46, 0)

def check_bot_running():
    """Check if the bot is still running"""
    try:
        with open('bot_pid.txt', 'r') as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    except:
        return False

def get_current_stats():
    """Get current session statistics"""
    stats = {
        'scans': 0,
        'opportunities': 0,
        'trades': 0,
        'profit': 0.0,
        'balance': 1000.0,
        'last_scan_time': 'N/A'
    }
    
    # Check paper trading log
    log_file = f"paper_trading_logs/paper_trading_log_{datetime.now().strftime('%Y-%m-%d')}.txt"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        # Count scans
        for line in lines:
            if '--- Scan #' in line:
                stats['scans'] += 1
                # Extract scan time
                if ' at ' in line:
                    stats['last_scan_time'] = line.split(' at ')[1].strip().replace(' ---', '')
            elif 'OPPORTUNITY FOUND' in line:
                stats['opportunities'] += 1
            elif 'TRADE EXECUTED' in line:
                stats['trades'] += 1
    
    # Check database
    db_file = 'data/trades.db'
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(*), SUM(profit)
                FROM trades
                WHERE DATE(timestamp) = ?
            """, (today,))
            
            result = cursor.fetchone()
            if result and result[0]:
                stats['trades'] = result[0]
                stats['profit'] = result[1] or 0.0
                stats['balance'] = 1000.0 + stats['profit']
            
            conn.close()
        except Exception as e:
            pass
    
    return stats

def generate_final_report():
    """Generate comprehensive final report"""
    stats = get_current_stats()
    
    report_content = f"""
{'='*70}
CRYPTO ARBITRAGE BOT - 55 MINUTE SESSION REPORT
{'='*70}

Session Information:
  Start Time: {START_TIME.strftime('%Y-%m-%d %H:%M:%S')}
  End Time: {END_TIME.strftime('%Y-%m-%d %H:%M:%S')}
  Duration: 55 minutes
  Mode: Paper Trading (Simulated)

Performance Metrics:
  Total Scans Completed: {stats['scans']}
  Opportunities Detected: {stats['opportunities']}
  Trades Executed: {stats['trades']}
  Total Profit/Loss: ${stats['profit']:.2f}
  Final Balance: ${stats['balance']:.2f}
  Starting Balance: $1,000.00
  Net Change: ${stats['balance'] - 1000:.2f} ({((stats['balance'] - 1000) / 1000 * 100):.2f}%)

Trading Configuration:
  Exchanges Monitored: Kraken, Coinbase, Bitstamp, Crypto.com
  Cryptocurrencies: BTC/USDT, ETH/USDT, BNB/USDT, ADA/USDT, SOL/USDT, DOT/USDT
  Min Profit Threshold: 1.0%
  Max Trade Amount: $10
  Daily Limit: $50

Status:
  Last Scan: {stats['last_scan_time']}
  Bot Status: {'Running' if check_bot_running() else 'Stopped'}

Notes:
  - This was a paper trading session (no real money involved)
  - Bitstamp API had authentication issues during this session
  - Email notifications were disabled due to SMTP configuration
  - The bot successfully monitored 3 exchanges (Kraken, Coinbase, Crypto.com)

{'='*70}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}
"""
    
    # Save to file
    report_file = f"/home/ubuntu/crypto_arbitrage_reports/session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    print(report_content)
    print(f"\nReport saved to: {report_file}")
    
    return report_file

def main():
    """Main monitoring loop"""
    print(f"Efficient Monitor Started at {datetime.now().strftime('%H:%M:%S')}")
    print(f"Bot started at: {START_TIME.strftime('%H:%M:%S')}")
    print(f"Expected end time: {END_TIME.strftime('%H:%M:%S')}")
    print("\nMonitoring bot session...")
    
    check_count = 0
    
    while True:
        now = datetime.now()
        
        # Check if we've reached the end time
        if now >= END_TIME:
            print(f"\n[{now.strftime('%H:%M:%S')}] 55 minutes elapsed!")
            break
        
        # Check every 5 minutes
        if check_count % 5 == 0:
            stats = get_current_stats()
            remaining = (END_TIME - now).total_seconds() / 60
            
            print(f"\n[{now.strftime('%H:%M:%S')}] Status Update ({remaining:.0f} min remaining):")
            print(f"  Scans: {stats['scans']}, Opportunities: {stats['opportunities']}, Trades: {stats['trades']}")
            print(f"  Balance: ${stats['balance']:.2f}, Profit: ${stats['profit']:.2f}")
            print(f"  Bot Running: {check_bot_running()}")
        
        time.sleep(60)  # Check every minute
        check_count += 1
    
    # Wait a bit for bot to finish stopping
    print("\nWaiting for bot to complete shutdown...")
    time.sleep(15)
    
    # Generate final report
    print("\nGenerating final report...")
    report_file = generate_final_report()
    
    print("\n✅ Session monitoring complete!")
    return report_file

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted. Generating report with current data...")
        generate_final_report()
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
