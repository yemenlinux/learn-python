# orphan_process_simple.py
import os
import time
import sys
import subprocess

def get_systemd_user_pid_subprocess():
    """Finds the PID of the systemd --user process using pgrep."""
    try:
        # pgrep -u $(whoami) systemd finds processes owned by the current user named "systemd"
        # The output needs to be decoded and split to get the first PID.
        output = subprocess.check_output(["pgrep", "-u", subprocess.getoutput("whoami"), "systemd"], stderr=subprocess.STDOUT, text=True)
        # Assuming the first PID is the user manager
        pids = output.strip().split('\n')
        return int(pids[0]) if pids[0] else None
    except subprocess.CalledProcessError as e:
        print(f"Error calling pgrep: {e.output}")
        return None
    except ValueError:
        print("pgrep returned unexpected output.")
        return None

def create_orphan_linux():
    """Create an orphan process on Unix-like systems (Linux/macOS)"""
    print("=== CREATING ORPHAN PROCESS (Linux/macOS) ===")
    
    pid = os.fork()
    
    if pid == 0:
        # Child process
        print(f"Child process: PID={os.getpid()}, Parent PID={os.getppid()}")
        
        # Simulate work
        for i in range(10):
            # Check parent PID - will change after parent dies
            current_ppid = os.getppid()
            
            print(f"Child PID: {current_ppid} is working... (iteration {i+1})")
            
            systemd_pid = get_systemd_user_pid_subprocess()
            print(f"systemd_pid: {systemd_pid}")
            if current_ppid == systemd_pid:
                print(f"  ⚠️  I'M NOW AN ORPHAN! child PID={os.getpid()} Parent was adopted by init (PID={systemd_pid})")
            else:
                print(f"  Parent PID: {current_ppid}")
            
            time.sleep(1)
        
        print("Child process exiting")
        sys.exit(0)
    
    else:
        # Parent process
        print(f"Parent process: PID={os.getpid()}, Created child PID={pid}")
        print("Parent will exit in 2 seconds, making child an orphan...")
        time.sleep(2)
        
        # Parent exits without waiting for child
        print("Parent process exiting (without waiting for child)")
        sys.exit(0)

def create_zombie_then_orphan():
    """Create a zombie that becomes orphaned"""
    print("\n=== ZOMBIE BECOMING ORPHAN ===")
    
    pid = os.fork()
    
    if pid == 0:
        # Child process
        print(f"Child (PID={os.getpid()}): I'm exiting immediately to become a zombie")
        sys.exit(0)
    
    else:
        # Parent process
        print(f"Parent (PID={os.getpid()}): Created child PID={pid}")
        print("Parent will sleep for 5 seconds without calling wait()...")
        
        # Parent doesn't call wait(), so child becomes zombie
        for i in range(20):
            print(f"Parent sleeping... {i+1}/5")
            time.sleep(1)
        
        print("Parent exiting without cleaning up child (zombie becomes orphan)")
        print("Run 'ps aux | grep defunct' to see the zombie")
        sys.exit(0)

if __name__ == "__main__":
    # Check if we're on a Unix-like system
    if hasattr(os, 'fork'):
        create_orphan_linux()
        
        # Uncomment to also create zombie example
        # time.sleep(3)
        # create_zombie_then_orphan()
    else:
        print("This example requires a Unix-like system with os.fork()") 
