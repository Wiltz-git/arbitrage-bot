#!/usr/bin/env python3
"""
Wait for the 55-minute bot session to complete and generate a trading report
"""

import time
import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

def check_bot_running():
    """Check if the bot is still running"""
    try:
        with open('bot_pid.txt', 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    except:
        return False

def get_session_stats():
    """Get statistics from the current session"""
    stats = {
        'scans': 0,
        'opportunities': 0,
        'trades': 0,
        'profit': 0.0,
        'balance': 1000.0
    }
    
    # Check paper trading log
    log_file = f"paper_trading_logs/paper_trading_log_{datetime.now().strftime('%Y-%m-%d')}.txt"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            content = f.read()
            stats['scans'] = content.count('--- Scan #')
            stats['opportunities'] = content.count('OPPORTUNITY FOUND')
            stats['trades'] = content.count('TRADE EXECUTED')
    
    # Check database for trade details
    db_file = 'data/trades.db'
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Get today's trades
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(*), SUM(profit), AVG(profit_percentage)
                FROM trades
                WHERE DATE(timestamp) = ?
            """, (today,))
            
            result = cursor.fetchone()
            if result and result[0]:
                stats['trades'] = result[0]
                stats['profit'] = result[1] or 0.0
            
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
    
    return stats

def generate_report():
    """Generate the final trading report"""
    print("\n" + "="*60)
    print("CRYPTO ARBITRAGE BOT - SESSION REPORT")
    print("="*60)
    
    stats = get_session_stats()
    
    print(f"\nSession Duration: 55 minutes")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n--- Performance Metrics ---")
    print(f"Total Scans: {stats['scans']}")
    print(f"Opportunities Found: {stats['opportunities']}")
    print(f"Trades Executed: {stats['trades']}")
    print(f"Total Profit: ${stats['profit']:.2f}")
    print(f"Current Balance: ${stats['balance']:.2f}")
    
    # Save report to file
    report_file = f"/home/ubuntu/crypto_arbitrage_reports/session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write("="*60 + "\n")
        f.write("CRYPTO ARBITRAGE BOT - SESSION REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Session Duration: 55 minutes\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\n--- Performance Metrics ---\n")
        f.write(f"Total Scans: {stats['scans']}\n")
        f.write(f"Opportunities Found: {stats['opportunities']}\n")
        f.write(f"Trades Executed: {stats['trades']}\n")
        f.write(f"Total Profit: ${stats['profit']:.2f}\n")
        f.write(f"Current Balance: ${stats['balance']:.2f}\n")
        f.write("\n" + "="*60 + "\n")
    
    print(f"\nReport saved to: {report_file}")
    print("="*60 + "\n")
    
    return report_file

def main():
    """Main function"""
    print("Waiting for 55-minute bot session to complete...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait for 55 minutes (3300 seconds)
    wait_time = 3300
    check_interval = 60  # Check every minute
    elapsed = 0
    
    while elapsed < wait_time:
        time.sleep(check_interval)
        elapsed += check_interval
        
        remaining = wait_time - elapsed
        minutes_remaining = remaining // 60
        
        if minutes_remaining % 5 == 0 and minutes_remaining > 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {minutes_remaining} minutes remaining...")
            
            # Show current stats
            stats = get_session_stats()
            print(f"  Current: {stats['scans']} scans, {stats['opportunities']} opportunities, {stats['trades']} trades")
    
    print("\n55 minutes elapsed! Generating final report...")
    
    # Wait a bit for the bot to finish stopping
    time.sleep(10)
    
    # Generate report
    report_file = generate_report()
    
    print("Session complete!")
    return report_file

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
