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
# SLIDES 41-42, 45-46: IMPLICIT THREADING & THREAD POOLS
# ============================================================================
print("\n" + "="*60)
print("SLIDES 41-42, 45-46: Implicit Threading & Thread Pools")
print("="*60)

def implicit_threading_demo():
    """
    Implicit threading: Let the system/library manage threads
    Thread pools: Reuse threads instead of creating/destroying
    """
    
    print("\n1. Thread Pools (concurrent.futures.ThreadPoolExecutor):")
    print("مثال على الاستخدام: توزيع مهام غير متجانسة ومن ثم معالجة النتائج")
    
    print("-" * 50)
    
    def task(name, duration):
        time.sleep(duration)
        return f"Task {name} completed in {duration}s"
    
    # Create thread pool
    with ThreadPoolExecutor(max_workers=3) as executor:
        print("Submitting 5 tasks to pool of 3 workers:")
        futures = []
        for i in range(5):
            duration = random.uniform(0.5, 1.5)
            future = executor.submit(task, i, duration)
            futures.append(future)
            print(f"  Submitted task {i}")
        
        print("\nResults:")
        for future in concurrent.futures.as_completed(futures):
            print(f"  {future.result()}")
    
    print("\n2. Fork-Join Parallelism:")
    print(" مثال على الاستخدام: تسريع خوارزميات البحث أو تسريع عملية محددة على بيانات قابلة للتجزئة")
    print("-" * 50)
    
    # Recursive task that splits work (like merge sort)
    def recursive_task(data, depth=0):
        if len(data) <= 2:  # Base case
            time.sleep(0.1)  # Simulate work
            return sum(data)
        
        # Split and process in parallel
        mid = len(data) // 2
        with ThreadPoolExecutor(max_workers=2) as executor:
            left_future = executor.submit(recursive_task, data[:mid], depth+1)
            right_future = executor.submit(recursive_task, data[mid:], depth+1)
            
            left_result = left_future.result()
            right_result = right_future.result()
            
            return left_result + right_result
    
    data = list(range(10))
    print(f"Processing list of {len(data)} elements with fork-join")
    result = recursive_task(data)
    print(f"Sum result: {result}")
    
    print("\n3. Python's concurrent.futures as Implicit Threading:")
    print("مثال على الاستخدام: تسريع عملية محددة على قائمة طويلة من البيانات")
    print("-" * 50)
    
    # Map function with thread pool
    def square(x):
        time.sleep(0.1)
        return x * x
    
    numbers = [1, 2, 3, 4, 5]
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(square, numbers))
        print(f"Squares of {numbers}: {results}")

implicit_threading_demo()
