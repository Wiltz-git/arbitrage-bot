import time
import os
import sys
from datetime import datetime, timedelta

start_time = datetime.now()
end_time = start_time + timedelta(minutes=55)
check_interval = 60  # Check every minute

print(f"Waiting for 55 minutes...")
print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

while datetime.now() < end_time:
    remaining = (end_time - datetime.now()).total_seconds()
    minutes_left = int(remaining / 60)
    
    if minutes_left % 5 == 0 and remaining % 60 < check_interval:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {minutes_left} minutes remaining...")
    
    time.sleep(check_interval)

print(f"\n55 minutes completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Monitoring complete!")
