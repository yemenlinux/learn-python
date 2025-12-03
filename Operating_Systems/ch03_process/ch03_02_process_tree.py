import os
import subprocess

def display_process_tree():
    """Display process tree similar to Linux pstree"""
    try:
        # Use pstree command to show process hierarchy
        result = subprocess.run(['pstree', '-s', str(os.getpid())], 
                              capture_output=True, text=True)
        print("Process Tree:")
        print(result.stdout)
    except FileNotFoundError:
        print("pstree command not available")
        # Alternative: show parent-child relationship
        print(f"Current PID: {os.getpid()}")
        print(f"Parent PID: {os.getppid()}")

display_process_tree()
