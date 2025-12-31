#!/usr/bin/env python3
"""
Monitor Linux scheduler activity
"""
import os
import time

def monitor_scheduler_stats(interval=2, count=5):
    """Monitor scheduler statistics"""
    for i in range(count):
        print(f"\n=== Iteration {i+1} ===")
        
        # Context switches
        with open('/proc/stat', 'r') as f:
            for line in f:
                if line.startswith('ctxt'):
                    print(f"Context switches: {line.split()[1]}")
                    break
        
        # Runqueue length
        with open('/proc/loadavg', 'r') as f:
            load = f.read().strip()
            print(f"Load average: {load}")
        
        # CPU utilization
        with open('/proc/uptime', 'r') as f:
            uptime, idle = f.read().split()
            print(f"System idle time: {float(idle):.2f}s")
        
        time.sleep(interval)

def check_process_scheduling(pid):
    """Check scheduling info for specific process"""
    try:
        # Scheduling policy
        policy_file = f'/proc/{pid}/sched'
        if os.path.exists(policy_file):
            print(f"\nScheduling info for PID {pid}:")
            with open(policy_file, 'r') as f:
                for line in f:
                    if any(key in line for key in ['policy', 'prio', 'vruntime', 'sum_exec_runtime']):
                        print(f"  {line.strip()}")
        
        # Nice value
        stat_file = f'/proc/{pid}/stat'
        if os.path.exists(stat_file):
            with open(stat_file, 'r') as f:
                fields = f.read().split()
                # Field 18 is nice value (adjust based on kernel)
                print(f"  Nice value: {fields[18]}")
                
    except Exception as e:
        print(f"Error checking PID {pid}: {e}")

if __name__ == "__main__":
    print("Linux Scheduler Monitoring")
    print("=" * 50)
    
    # Monitor overall stats
    monitor_scheduler_stats(interval=1, count=3)
    
    # Check self
    check_process_scheduling(os.getpid()) 
