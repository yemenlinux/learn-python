"""
COMPREHENSIVE THREADS & CONCURRENCY CONCEPTS IN PYTHON
Corresponding to Lecture Chapter 4

This script demonstrates key threading and concurrency concepts
from the Operating System Concepts textbook using Python.
"""

import threading
import multiprocessing
import concurrent.futures
import time
import random
import queue
from threading import Thread, Lock, Condition, Semaphore, local as thread_local
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial

print("=" * 60)
print("THREADS & CONCURRENCY: PYTHON EXAMPLES")
print("=" * 60)

# ============================================================================
# SLIDES 66-70: OS EXAMPLES (Windows/Linux Threads in Python Context)
# ============================================================================
print("\n" + "="*60)
print("SLIDES 66-70: OS Examples in Python Context")
print("="*60)

def os_specific_info():
    """
    How Python threading interacts with different OS
    """
    
    print("\nHow Python Threads Map to OS Threads:")
    print("-" * 50)
    
    print("\nOn Windows:")
    print("  - Python threads map to Windows kernel threads (1:1 model)")
    print("  - Each thread has its own stack in kernel space")
    print("  - Thread scheduling handled by Windows kernel")
    
    print("\nOn Linux:")
    print("  - Python threads are pthreads (POSIX threads)")
    print("  - Implemented as lightweight processes (LWPs)")
    print("  - Share same memory space (CLONE_VM flag in clone())")
    
    print("\nCross-platform Python code:")
    print("  - threading module provides consistent interface")
    print("  - OS differences mostly abstracted away")
    print("  - multiprocessing uses fork() on Unix, spawn() on Windows")
    
    # Show current process/thread info
    print(f"\nCurrent Process ID: {multiprocessing.current_process().pid}")
    print(f"Current Thread: {threading.current_thread().name}")
    print(f"Active Threads: {threading.active_count()}")
    
    # Demonstrate OS-agnostic thread creation
    print("\nCreating OS-agnostic threads in Python:")
    
    def os_agnostic_worker():
        print(f"  Running on thread: {threading.current_thread().name}")
        print(f"  Process ID: {multiprocessing.current_process().pid}")
    
    threads = [Thread(target=os_agnostic_worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

os_specific_info()
