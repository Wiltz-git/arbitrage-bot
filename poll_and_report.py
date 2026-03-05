#!/usr/bin/env python3
"""
Poll for bot completion and generate report immediately
"""
import time
import os
import sys
from datetime import datetime

def main():
    print("Polling for bot completion...")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Poll every 10 seconds
    poll_interval = 10
    max_wait = 3700  # 61 minutes max
    elapsed = 0
    
    while elapsed < max_wait:
        # Check for completion flag
        if os.path.exists('monitoring_complete.flag'):
            print(f"\n✅ Bot completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("Generating report...")
            
            # Run report generation
            os.system('python3 wait_and_generate_report.py')
            sys.exit(0)
        
        # Show progress
        minutes = elapsed // 60
        seconds = elapsed % 60
        print(f"Waiting... {minutes:02d}:{seconds:02d} elapsed", end='\r')
        
        time.sleep(poll_interval)
        elapsed += poll_interval
    
    print("\n⚠️ Timeout reached - generating report anyway")
    os.system('python3 wait_and_generate_report.py')

if __name__ == '__main__':
    main()
