import os
import time

def child_process():
    """Child process example using fork()"""
    pid = os.fork()
    
    if pid == 0:
        # Child process
        print(f"Child Process: PID = {os.getpid()}, Parent PID = {os.getppid()}")
        time.sleep(2)
        print("Child process exiting")
        os._exit(0)  # Child exits
    else:
        # Parent process
        print(f"Parent Process: PID = {os.getpid()}, Created Child PID = {pid}")
        # Wait for child to complete (like wait() system call)
        child_pid, status = os.wait()
        print(f"Parent: Child {child_pid} finished with status {status}")

child_process() 
