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
# SLIDES 17-20: USER THREADS VS KERNEL THREADS
# ============================================================================
print("\n" + "="*60)
print("SLIDES 17-20: User Threads vs Kernel Threads")
print("="*60)

# Demonstrate the difference
print("\nDemonstration: GIL limitation in Python threads")

shared_counter = 0
lock = Lock()

# Using threads (user-level)
def increment_counter(n):
    global shared_counter
    for _ in range(n):
        with lock:  # Need lock due to GIL
            shared_counter += 1
            
# Using processes (kernel-level)
def increment_process(n, return_dict, pid):
    local_counter = 0
    for _ in range(n):
        local_counter += 1
    return_dict[pid] = local_counter
    
    

def user_vs_kernel_threads():
    """
    In Python:
    - threading module → User-level threads (managed by Python runtime)
    - multiprocessing module → Kernel-level threads/processes (managed by OS)
    """
    
    print("\nPython's Implementation:")
    print("-" * 50)
    print("User-level Threads (threading module):")
    print("  - Managed by Python interpreter")
    print("  - Subject to GIL (Global Interpreter Lock)")
    print("  - Good for I/O-bound tasks")
    print("  - Lightweight, quick to create")
    
    print("\nKernel-level Processes (multiprocessing module):")
    print("  - Managed by operating system")
    print("  - Each process has its own Python interpreter")
    print("  - No GIL limitations")
    print("  - Good for CPU-bound tasks")
    print("  - Heavier, more overhead")
    
#     # Demonstrate the difference
#     print("\nDemonstration: GIL limitation in Python threads")
#     
#     shared_counter = 0
#     lock = Lock()
#     
#     def increment_counter(n):
#         global shared_counter
#         for _ in range(n):
#             with lock:  # Need lock due to GIL
#                 shared_counter += 1
    
    # Using threads (user-level)
    start = time.time()
    threads = []
    for _ in range(4):
        t = Thread(target=increment_counter, args=(100_000,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    thread_time = time.time() - start
    print(f"Threads completed in {thread_time:.2f}s, Counter: {shared_counter}")
    
    # # Using processes (kernel-level)
    # def increment_process(n, return_dict, pid):
    #     local_counter = 0
    #     for _ in range(n):
    #         local_counter += 1
    #     return_dict[pid] = local_counter
    
    start = time.time()
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []
    
    for i in range(4):
        p = multiprocessing.Process(target=increment_process, 
                                   args=(100_000, return_dict, i))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    # print(return_dict)
    
    process_total = sum(return_dict.values())
    process_time = time.time() - start
    print(f"Processes completed in {process_time:.2f}s, Total: {process_total}")

user_vs_kernel_threads()
