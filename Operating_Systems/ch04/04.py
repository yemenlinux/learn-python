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
# SLIDES 14-15: AMDHAH'S LAW
# ============================================================================
print("\n" + "="*60)
print("SLIDES 14-15: Amdahl's Law")
print("="*60)

def amdahls_law_demo():
    """
    Amdahl's Law: Speedup ≤ 1 / (S + (1-S)/N)
    Where S = serial portion, N = number of processors
    """
    
    def calculate_speedup(serial_fraction, num_cores):
        """Calculate theoretical speedup based on Amdahl's Law"""
        if serial_fraction == 0:
            return num_cores  # Perfect parallelization
        return 1 / (serial_fraction + (1 - serial_fraction) / num_cores)
    
    print("\nAmdahl's Law Examples:")
    print("-" * 40)
    print("Serial Portion | Cores | Speedup")
    print("-" * 40)
    
    test_cases = [
        (0.25, 2),   # 25% serial, 2 cores
        (0.25, 4),   # 25% serial, 4 cores
        (0.25, 8),   # 25% serial, 8 cores
        (0.10, 4),   # 10% serial, 4 cores
        (0.50, 4),   # 50% serial, 4 cores
    ]
    
    for S, N in test_cases:
        speedup = calculate_speedup(S, N)
        print(f"    {S*100:3.0f}%      |   {N:2d}  |   {speedup:.2f}x")
    
    # Practical demonstration
    print("\nPractical Example: Image Processing")
    print("(Simulating with time.sleep)")
    
    def serial_portion():
        time.sleep(0.2)  # Serial part
    
    def parallelizable_portion(work_units):
        time.sleep(0.2 * work_units)
    
    # Single core
    start = time.time()
    serial_portion()
    parallelizable_portion(1)
    single_time = time.time() - start
    
    # Four cores (theoretically)
    start = time.time()
    # serial_portion() # لاحظ أننا حسبنا زمن التنفيذ لعملية واحدة كاملة مع التوازي أيضاً
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Divide work among 4 threads
        futures = [executor.submit(parallelizable_portion, 0.25) for _ in range(4)]
        for f in futures:
            f.result()
    multi_time = time.time() - start
    
    print(f"\nSingle core time: {single_time:.2f}s")
    print(f"Four cores time: {multi_time:.2f}s")
    print(f"Actual speedup: {single_time/multi_time:.2f}x")
    print(" لاحظ أننا حسبنا زمن التنفيذ لعملية واحدة كاملة مع التوازي أيضاً")

amdahls_law_demo()
