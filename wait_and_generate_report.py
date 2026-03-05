#!/usr/bin/env python3
"""
Wait for bot completion and generate trading report
"""
import time
import os
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

def check_completion():
    """Check if monitoring is complete"""
    return os.path.exists('monitoring_complete.flag')

def get_bot_status():
    """Check if bot is still running"""
    try:
        with open('bot_pid.txt', 'r') as f:
            pid = int(f.read().strip())
        # Check if process exists
        os.kill(pid, 0)
        return True
    except:
        return False

def generate_report():
    """Generate trading summary report"""
    print("Generating trading report...")
    
    # Connect to database
    db_path = 'data/trades.db'
    if not os.path.exists(db_path):
        print("No database found - no trades recorded")
        return create_empty_report()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Query opportunities found
    cursor.execute("""
        SELECT COUNT(*), AVG(profit_percentage), MAX(profit_percentage)
        FROM opportunities
        WHERE DATE(timestamp) = ?
    """, (today,))
    
    opp_result = cursor.fetchone()
    opportunities_count = opp_result[0] if opp_result[0] else 0
    avg_profit = opp_result[1] if opp_result[1] else 0
    max_profit = opp_result[2] if opp_result[2] else 0
    
    # Query trades executed
    cursor.execute("""
        SELECT COUNT(*), SUM(profit_usd), AVG(profit_usd)
        FROM trades
        WHERE DATE(timestamp) = ? AND status = 'completed'
    """, (today,))
    
    trade_result = cursor.fetchone()
    trades_count = trade_result[0] if trade_result[0] else 0
    total_profit = trade_result[1] if trade_result[1] else 0
    avg_trade_profit = trade_result[2] if trade_result[2] else 0
    
    # Get trade details
    cursor.execute("""
        SELECT symbol, buy_exchange, sell_exchange, profit_usd, profit_percentage, timestamp
        FROM trades
        WHERE DATE(timestamp) = ? AND status = 'completed'
        ORDER BY profit_usd DESC
        LIMIT 10
    """, (today,))
    
    top_trades = cursor.fetchall()
    
    # Get exchange statistics
    cursor.execute("""
        SELECT buy_exchange, COUNT(*) as buy_count
        FROM trades
        WHERE DATE(timestamp) = ? AND status = 'completed'
        GROUP BY buy_exchange
    """, (today,))
    
    buy_stats = cursor.fetchall()
    
    cursor.execute("""
        SELECT sell_exchange, COUNT(*) as sell_count
        FROM trades
        WHERE DATE(timestamp) = ? AND status = 'completed'
        GROUP BY sell_exchange
    """, (today,))
    
    sell_stats = cursor.fetchall()
    
    conn.close()
    
    # Create report
    report = {
        'date': today,
        'session_duration': '55 minutes',
        'summary': {
            'opportunities_found': opportunities_count,
            'trades_executed': trades_count,
            'total_profit_usd': round(total_profit, 2),
            'average_profit_per_trade': round(avg_trade_profit, 2),
            'average_opportunity_profit': round(avg_profit, 2),
            'max_opportunity_profit': round(max_profit, 2)
        },
        'top_trades': [
            {
                'symbol': t[0],
                'buy_exchange': t[1],
                'sell_exchange': t[2],
                'profit_usd': round(t[3], 2),
                'profit_percentage': round(t[4], 2),
                'timestamp': t[5]
            }
            for t in top_trades
        ],
        'exchange_stats': {
            'buy_operations': {ex: count for ex, count in buy_stats},
            'sell_operations': {ex: count for ex, count in sell_stats}
        }
    }
    
    return report

def create_empty_report():
    """Create report when no trades occurred"""
    today = datetime.now().strftime('%Y-%m-%d')
    return {
        'date': today,
        'session_duration': '55 minutes',
        'summary': {
            'opportunities_found': 0,
            'trades_executed': 0,
            'total_profit_usd': 0,
            'average_profit_per_trade': 0,
            'average_opportunity_profit': 0,
            'max_opportunity_profit': 0
        },
        'top_trades': [],
        'exchange_stats': {
            'buy_operations': {},
            'sell_operations': {}
        },
        'note': 'No profitable arbitrage opportunities found during this session'
    }

def create_markdown_report(report_data):
    """Create markdown formatted report"""
    md = f"""# Crypto Arbitrage Bot - Trading Session Report

**Date:** {report_data['date']}  
**Session Duration:** {report_data['session_duration']}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## Executive Summary

- **Opportunities Found:** {report_data['summary']['opportunities_found']}
- **Trades Executed:** {report_data['summary']['trades_executed']}
- **Total Profit:** ${report_data['summary']['total_profit_usd']:.2f}
- **Average Profit per Trade:** ${report_data['summary']['average_profit_per_trade']:.2f}
- **Average Opportunity Profit:** {report_data['summary']['average_opportunity_profit']:.2f}%
- **Maximum Opportunity Profit:** {report_data['summary']['max_opportunity_profit']:.2f}%

---

## Top Trades

"""
    
    if report_data['top_trades']:
        for i, trade in enumerate(report_data['top_trades'], 1):
            md += f"""
### Trade #{i}
- **Symbol:** {trade['symbol']}
- **Buy Exchange:** {trade['buy_exchange']}
- **Sell Exchange:** {trade['sell_exchange']}
- **Profit:** ${trade['profit_usd']:.2f} ({trade['profit_percentage']:.2f}%)
- **Time:** {trade['timestamp']}

"""
    else:
        md += "\n*No trades executed during this session*\n\n"
    
    md += """---

## Exchange Activity

### Buy Operations
"""
    
    if report_data['exchange_stats']['buy_operations']:
        for exchange, count in report_data['exchange_stats']['buy_operations'].items():
            md += f"- **{exchange}:** {count} trades\n"
    else:
        md += "*No buy operations*\n"
    
    md += "\n### Sell Operations\n"
    
    if report_data['exchange_stats']['sell_operations']:
        for exchange, count in report_data['exchange_stats']['sell_operations'].items():
            md += f"- **{exchange}:** {count} trades\n"
    else:
        md += "*No sell operations*\n"
    
    if 'note' in report_data:
        md += f"\n---\n\n## Note\n\n{report_data['note']}\n"
    
    md += """
---

## Bot Configuration

- **Mode:** Paper Trading (Simulated)
- **Exchanges:** Kraken, Coinbase, Bitstamp, Crypto.com
- **Tracked Pairs:** BTC/USDT, ETH/USDT, BNB/USDT, ADA/USDT, SOL/USDT, DOT/USDT
- **Minimum Profit Threshold:** 1.0%
- **Max Trade Amount:** $10 (Trial Mode)
- **Daily Limit:** $50

---

*Report generated by Crypto Arbitrage Bot*
"""
    
    return md

def main():
    print("Waiting for bot to complete 55-minute session...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait for completion flag or timeout (60 minutes max)
    timeout = 3600  # 60 minutes
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if check_completion():
            print("\nBot session completed!")
            break
        
        # Check every 30 seconds
        time.sleep(30)
        
        # Show progress
        elapsed = int(time.time() - start_time)
        print(f"Elapsed: {elapsed//60} minutes, Bot running: {get_bot_status()}", end='\r')
    
    # Generate report
    print("\n\nGenerating report...")
    report_data = generate_report()
    
    # Save JSON report
    json_path = '/home/ubuntu/crypto_arbitrage_reports/trading_report.json'
    with open(json_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    print(f"JSON report saved: {json_path}")
    
    # Save Markdown report
    md_report = create_markdown_report(report_data)
    md_path = '/home/ubuntu/crypto_arbitrage_reports/trading_report.md'
    with open(md_path, 'w') as f:
        f.write(md_report)
    print(f"Markdown report saved: {md_path}")
    
    print("\n✅ Report generation complete!")
    print(f"\nSummary:")
    print(f"  - Opportunities: {report_data['summary']['opportunities_found']}")
    print(f"  - Trades: {report_data['summary']['trades_executed']}")
    print(f"  - Profit: ${report_data['summary']['total_profit_usd']:.2f}")

if __name__ == '__main__':
    main()
