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
# SLIDES 7-8: THREADS VS PROCESSES & BENEFITS
# ============================================================================
print("\n" + "="*60)
print("SLIDES 7-8: Threads vs Processes & Benefits")
print("="*60)

def compare_threads_processes():
    print("\nSingle-threaded vs Multi-threaded Processes:")
    
    # Single-threaded task
    def single_threaded_task():
        results = []
        for i in range(3):
            # السطر التالي ينام نصف ثانية كمثال لعملية تستغرق نصف ثانية. يمكنك أن تكتب هنا أي عملية أخرى
            time.sleep(0.5)  # Simulate work
            results.append(f"Task {i}")
        return results
    
    # Multi-threaded version
    def worker(task_id, results_list, lock):
        time.sleep(0.5)  # Simulate work
        with lock:
            results_list.append(f"Task {task_id}")
    
    # Run single-threaded
    start = time.time()
    single_results = single_threaded_task()
    single_time = time.time() - start
    
    # Run multi-threaded
    start = time.time()
    results = []
    lock = Lock()
    threads = []
    
    for i in range(3):
        t = Thread(target=worker, args=(i, results, lock))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    multi_time = time.time() - start
    
    print(f"Single-threaded time: {single_time:.2f}s, Results: {single_results}")
    print(f"Multi-threaded time: {multi_time:.2f}s, Results: {results}")
    print("\nBenefits demonstrated:")
    print("1. Responsiveness: Tasks complete faster")
    print("2. Resource Sharing: Threads share 'results' list")
    print("3. Economy: Thread creation cheaper than process creation")

compare_threads_processes()
