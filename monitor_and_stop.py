#!/usr/bin/env python3
"""
Monitor the bot for 55 minutes and then stop it gracefully
"""
import time
import os
import signal
import sys
from datetime import datetime, timedelta

def main():
    # Read bot PID
    try:
        with open('bot_pid.txt', 'r') as f:
            bot_pid = int(f.read().strip())
    except:
        print("Error: Could not read bot PID")
        sys.exit(1)
    
    # Calculate end time
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=55)
    
    print(f"Bot monitoring started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bot will run until {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring bot PID: {bot_pid}")
    
    # Wait for 55 minutes (3300 seconds)
    time.sleep(3300)
    
    # Stop the bot
    print(f"\n55 minutes elapsed. Stopping bot (PID: {bot_pid})...")
    try:
        os.kill(bot_pid, signal.SIGTERM)
        print("Bot stopped successfully")
        
        # Create completion flag
        with open('monitoring_complete.flag', 'w') as f:
            f.write(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
    except ProcessLookupError:
        print("Bot process not found (may have already stopped)")
    except Exception as e:
        print(f"Error stopping bot: {e}")
    
    print("Monitoring complete")

if __name__ == '__main__':
    main()
