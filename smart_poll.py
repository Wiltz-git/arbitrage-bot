#!/usr/bin/env python3
import time
import os
import sys
from datetime import datetime, timedelta

# Calculate when bot should complete
start_time = datetime(2026, 1, 27, 13, 46, 9)
end_time = start_time + timedelta(minutes=55)
now = datetime.now()

print(f"Smart polling started at {now.strftime('%H:%M:%S')}")
print(f"Bot should complete at {end_time.strftime('%H:%M:%S')}")

# Calculate remaining seconds
remaining = (end_time - now).total_seconds()
print(f"Remaining time: {int(remaining/60)} minutes {int(remaining%60)} seconds")
print()

if remaining > 0:
    print("Waiting for completion...")
    # Sleep until 30 seconds before expected completion
    if remaining > 30:
        time.sleep(remaining - 30)
    
    # Poll every 5 seconds for the last 30 seconds
    while True:
        if os.path.exists('monitoring_complete.flag'):
            print("\n✅ Completion flag detected!")
            break
        
        now = datetime.now()
        if now >= end_time + timedelta(seconds=30):
            print("\n⏰ Time exceeded, proceeding anyway")
            break
        
        time.sleep(5)
        print(".", end="", flush=True)

print("\nGenerating final report...")
os.system('python3 wait_and_generate_report.py')
print("Done!")
