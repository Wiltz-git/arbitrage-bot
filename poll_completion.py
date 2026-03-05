#!/usr/bin/env python3
"""
Poll for completion of the 55-minute bot run
"""
import time
import os
from datetime import datetime, timedelta

# Bot start time
start_time = datetime.strptime("2026-01-27 12:40:45", "%Y-%m-%d %H:%M:%S")
end_time = start_time + timedelta(minutes=55)

print(f"Polling for completion...")
print(f"Target end time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

check_count = 0
while True:
    current_time = datetime.now()
    
    # Check if completion status file exists
    if os.path.exists('completion_status.txt'):
        with open('completion_status.txt', 'r') as f:
            status = f.read().strip()
            if status == 'COMPLETE':
                print(f"\n✓ Bot run completed at {current_time.strftime('%H:%M:%S')}")
                break
    
    # Check if we've reached the end time
    if current_time >= end_time:
        print(f"\n✓ Target time reached at {current_time.strftime('%H:%M:%S')}")
        break
    
    # Show progress every 5 minutes
    remaining = (end_time - current_time).total_seconds() / 60
    if check_count % 5 == 0:  # Every 5 checks (5 minutes)
        elapsed = (current_time - start_time).total_seconds() / 60
        print(f"[{current_time.strftime('%H:%M:%S')}] Elapsed: {elapsed:.1f}m | Remaining: {remaining:.1f}m")
    
    check_count += 1
    time.sleep(60)  # Check every minute

print("\nBot run monitoring complete!")
