#!/usr/bin/env python3
"""
Final wait for 55-minute completion and generate report
"""
import time
import os
import subprocess
from datetime import datetime, timedelta

# Configuration
start_time = datetime.strptime("2026-01-27 12:40:45", "%Y-%m-%d %H:%M:%S")
end_time = start_time + timedelta(minutes=55)
log_file = "bot_run_20260127_124045.log"

print("=== Final Wait for 55-Minute Bot Run ===")
print(f"Target completion: {end_time.strftime('%H:%M:%S')}")

# Wait until end time
while datetime.now() < end_time:
    remaining = (end_time - datetime.now()).total_seconds()
    if remaining > 0:
        # Sleep in chunks to avoid timeout
        sleep_time = min(remaining, 300)  # Max 5 minutes at a time
        time.sleep(sleep_time)

print(f"\n✓ 55 minutes complete at {datetime.now().strftime('%H:%M:%S')}")

# Stop the bot
print("\nStopping bot...")
try:
    result = subprocess.run(['pkill', '-SIGINT', '-f', 'python.*main.py'], 
                          capture_output=True, text=True)
    time.sleep(5)
    
    # Force kill if still running
    subprocess.run(['pkill', '-9', '-f', 'python.*main.py'], 
                  capture_output=True, text=True)
    print("✓ Bot stopped")
except Exception as e:
    print(f"Error stopping bot: {e}")

# Mark completion
with open('completion_status.txt', 'w') as f:
    f.write('COMPLETE')

print("\n✓ Bot run complete!")
print(f"Log file: {log_file}")
print(f"Log size: {os.path.getsize(log_file):,} bytes")
