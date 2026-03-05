#!/usr/bin/env python3
"""
Wait for the 55-minute bot run and provide periodic updates
"""
import time
import subprocess
import os
from datetime import datetime, timedelta

# Bot start time
START_TIME = datetime.now()
END_TIME = START_TIME + timedelta(minutes=55)
LOG_FILE = "bot_run_20260127_124045.log"

print(f"=== Waiting for 55-minute bot run ===")
print(f"Start time: {START_TIME.strftime('%H:%M:%S')}")
print(f"End time: {END_TIME.strftime('%H:%M:%S')}")
print(f"Duration: 55 minutes")
print()

# Check every 5 minutes
check_interval = 300  # 5 minutes in seconds
last_check = START_TIME

while datetime.now() < END_TIME:
    current_time = datetime.now()
    elapsed = (current_time - START_TIME).total_seconds() / 60
    remaining = (END_TIME - current_time).total_seconds() / 60
    
    if (current_time - last_check).total_seconds() >= check_interval or elapsed < 1:
        print(f"\n--- Status Update at {current_time.strftime('%H:%M:%S')} ---")
        print(f"Elapsed: {elapsed:.1f} minutes | Remaining: {remaining:.1f} minutes")
        
        # Check if bot is still running
        try:
            result = subprocess.run(['pgrep', '-f', 'python.*main.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Bot is running")
                
                # Show recent log entries
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, 'r') as f:
                        lines = f.readlines()
                        recent_lines = lines[-5:] if len(lines) >= 5 else lines
                        print("\nRecent activity:")
                        for line in recent_lines:
                            print(f"  {line.strip()}")
            else:
                print("✗ Bot has stopped!")
                break
        except Exception as e:
            print(f"Error checking bot status: {e}")
        
        last_check = current_time
    
    # Sleep for 1 minute before next check
    time.sleep(60)

print(f"\n=== 55-minute period complete at {datetime.now().strftime('%H:%M:%S')} ===")
