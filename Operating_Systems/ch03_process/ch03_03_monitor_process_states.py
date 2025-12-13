import os
import subprocess
import time

def monitor_process_states():
    """Monitor process states and information"""
    
    def get_process_info(pid):
        """Get detailed information about a process"""
        try:
            # Read from /proc filesystem
            with open(f"/proc/{pid}/status", 'r') as f:
                status = f.read()
            
            with open(f"/proc/{pid}/stat", 'r') as f:
                stat = f.read().split()
            
            return {
                'pid': pid,
                'state': stat[2],  # Process state
                'ppid': stat[3],   # Parent PID
                'priority': stat[17]  # Priority
            }
        except:
            return None
    
    # Create a child process and monitor it
    pid = os.fork()
    
    if pid == 0:
        # Child process - do some work
        print(f"Child process {os.getpid()} running...")
        for i in range(5):
            print(f"Child working... {i}")
            time.sleep(1)
        os._exit(0)
    else:
        # Parent process - monitor child
        print(f"Parent monitoring child {pid}")
        
        while True:
            info = get_process_info(pid)
            if info:
                state_map = {
                    'R': 'Running',
                    'S': 'Sleeping',
                    'D': 'Disk Sleep',
                    'Z': 'Zombie',
                    'T': 'Stopped'
                }
                state = state_map.get(info['state'], info['state'])
                print(f"PID {info['pid']} State: {state}")
            
            # Check if child still exists
            try:
                os.kill(pid, 0)  # Check if process exists
            except OSError:
                print("Child process has terminated")
                break
            
            time.sleep(0.5)

# monitor_process_states()


#######################

def monitor_process_states_fixed1():
    """Monitor process states without creating zombies"""
    
    def get_process_info(pid):
        """Get detailed information about a process"""
        try:
            with open(f"/proc/{pid}/stat", 'r') as f:
                stat = f.read().split()
            
            return {
                'pid': pid,
                'state': stat[2],  # Process state
                'ppid': stat[3],   # Parent PID
            }
        except:
            return None
    
    # Create a child process and monitor it
    pid = os.fork()
    
    if pid == 0:
        # Child process - do some work
        print(f"Child process {os.getpid()} running...")
        for i in range(3):  # Reduced for demonstration
            print(f"Child working... {i}")
            time.sleep(1)
        print("Child process exiting normally")
        os._exit(0)
    else:
        # Parent process - monitor child
        print(f"Parent monitoring child {pid}")
        child_exited = False
        
        while not child_exited:
            info = get_process_info(pid)
            if info:
                state_map = {
                    'R': 'Running',
                    'S': 'Sleeping', 
                    'D': 'Disk Sleep',
                    'Z': 'Zombie',
                    'T': 'Stopped'
                }
                state = state_map.get(info['state'], info['state'])
                print(f"PID {info['pid']} State: {state}")
                
                # If child becomes zombie, we should wait for it
                if info['state'] == 'Z':
                    print("Child became zombie - waiting to collect exit status...")
                    break
            else:
                print("Cannot get process info - child may have terminated")
                break
            
            # Try non-blocking wait to check if child exited
            try:
                # WNOHANG means don't block if child hasn't exited
                waited_pid, status = os.waitpid(pid, os.WNOHANG)
                if waited_pid == pid:
                    print(f"Child {pid} exited with status {status}")
                    child_exited = True
                    break
            except ChildProcessError:
                print("Child process already reaped")
                child_exited = True
                break
                
            time.sleep(0.5)
        
        # Final cleanup - make sure we collect the child
        try:
            waited_pid, status = os.waitpid(pid, os.WNOHANG)
            if waited_pid == pid:
                print(f"Final cleanup: Child {pid} collected")
        except ChildProcessError:
            print("Child already collected")

# Test the fixed version
monitor_process_states_fixed1()
