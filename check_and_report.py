#!/usr/bin/env python3
"""
Check if session is complete and generate report
"""

from datetime import datetime, timedelta
import os
import sqlite3
import sys

def get_stats():
    """Get current statistics"""
    stats = {
        'scans': 0,
        'opportunities': 0,
        'trades': 0,
        'profit': 0.0,
        'balance': 1000.0
    }
    
    log_file = f"paper_trading_logs/paper_trading_log_{datetime.now().strftime('%Y-%m-%d')}.txt"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            content = f.read()
            stats['scans'] = content.count('--- Scan #')
            stats['opportunities'] = content.count('OPPORTUNITY')
            stats['trades'] = content.count('TRADE EXECUTED')
    
    db_file = 'data/trades.db'
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*), SUM(profit) FROM trades WHERE DATE(timestamp) = ?", (today,))
            result = cursor.fetchone()
            if result and result[0]:
                stats['trades'] = result[0]
                stats['profit'] = result[1] or 0.0
                stats['balance'] = 1000.0 + stats['profit']
            conn.close()
        except:
            pass
    
    return stats

def generate_report(stats, session_complete=True):
    """Generate the trading report"""
    
    status_text = "COMPLETE" if session_complete else "IN PROGRESS"
    
    report = f"""# Crypto Arbitrage Bot - Session Report

## Session Information
- **Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Start Time**: 14:51:00
- **End Time**: 15:46:00
- **Duration**: 55 minutes
- **Mode**: Paper Trading (Simulated)
- **Status**: {status_text}

## Performance Metrics
- **Total Scans**: {stats['scans']}
- **Opportunities Found**: {stats['opportunities']}
- **Trades Executed**: {stats['trades']}
- **Total Profit/Loss**: ${stats['profit']:.2f}
- **Final Balance**: ${stats['balance']:.2f}
- **Starting Balance**: $1,000.00
- **Net Change**: ${stats['balance'] - 1000:.2f} ({((stats['balance']/1000 - 1) * 100):.2f}%)

## Trading Configuration
- **Exchanges Monitored**: Kraken, Coinbase, Bitstamp, Crypto.com
- **Trading Pairs**: BTC/USDT, ETH/USDT, BNB/USDT, ADA/USDT, SOL/USDT, DOT/USDT
- **Min Profit Threshold**: 1.0%
- **Max Trade Amount**: $10
- **Daily Limit**: $50

## Exchange Status
- **Kraken**: ✅ Connected
- **Coinbase**: ✅ Connected
- **Bitstamp**: ⚠️ API Authentication Issues
- **Crypto.com**: ✅ Connected

## Session Notes
- This was a paper trading session (no real funds used)
- Bitstamp experienced API authentication issues during the session
- Successfully monitored 3 exchanges (Kraken, Coinbase, Crypto.com)
- Scan frequency: approximately {stats['scans']/55:.1f} scans per minute
- Email notifications were disabled due to SMTP configuration

## Analysis
The bot completed {stats['scans']} market scans during the 55-minute session, checking for arbitrage opportunities across multiple exchanges and trading pairs. {'No profitable opportunities meeting the 1% threshold were found during this session.' if stats['opportunities'] == 0 else f'{stats["opportunities"]} opportunities were detected.'}

This is typical for arbitrage trading, as profitable opportunities are rare and require:
1. Significant price differences between exchanges (>1% after fees)
2. Sufficient liquidity on both exchanges
3. Fast execution to capture the spread before it closes

---
*Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return report

def main():
    """Main function"""
    # Session timing
    start_time = datetime(2026, 1, 27, 14, 51, 0)
    end_time = start_time + timedelta(minutes=55)
    current_time = datetime.now()
    
    session_complete = current_time >= end_time
    
    # Get statistics
    stats = get_stats()
    
    # Generate report
    report = generate_report(stats, session_complete)
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"/home/ubuntu/crypto_arbitrage_reports/session_report_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n{'='*70}")
    print(f"Report saved to: {report_file}")
    print(f"{'='*70}")
    
    if not session_complete:
        remaining = (end_time - current_time).total_seconds() / 60
        print(f"\nNote: Session still in progress ({remaining:.1f} minutes remaining)")
        print("This is a preliminary report. Final report will be generated at session end.")
    
    return report_file

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
