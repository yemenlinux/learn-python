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
# SLIDES 10-13: MULTICORE PROGRAMMING & PARALLELISM
# ============================================================================
print("\n" + "="*60)
print("SLIDES 10-13: Multicore Programming & Parallelism")
print("="*60)

# CONCURRENCY on single core (threading - I/O bound)
def io_bound_task(task_id):
    time.sleep(1)  # Simulate I/O wait
    return f"I/O Task {task_id}"


# PARALLELISM on multiple cores (multiprocessing - CPU bound)
def cpu_intensive_task(n):
    # Simulate CPU work
    result = sum(i*i for i in range(n))
    return result



def demonstrate_parallelism():
    print("\nDemonstrating Concurrency vs Parallelism:")
    print("(Note: Python has GIL - Global Interpreter Lock)")
    print("For true CPU parallelism, we use multiprocessing")
    
    # # CONCURRENCY on single core (threading - I/O bound)
    # def io_bound_task(task_id):
    #     time.sleep(1)  # Simulate I/O wait
    #     return f"I/O Task {task_id}"
    
    # # PARALLELISM on multiple cores (multiprocessing - CPU bound)
    # def cpu_intensive_task(n):
    #     # Simulate CPU work
    #     result = sum(i*i for i in range(n))
    #     return result
    
    print("\n1. CONCURRENCY (I/O bound tasks with threading):")
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(io_bound_task, i) for i in range(4)]
        results = [f.result() for f in futures]
    print(f"   Completed 4 I/O tasks in {time.time() - start:.2f}s")
    print(f"results = {results}")
    print("لاحظ أن تنفيذ أربع عمليات استغرق ثانية واحدة بدلاً عن 4 ثواني في حال التنفيذ المتتالي.")
    
    print("\n2. PARALLELISM (CPU bound tasks without multiprocessing):")
    start = time.time()
    result = cpu_intensive_task(1_000_000)
    print(f"   Completed 1 CPU task in {time.time() - start:.2f}s")
    print(f"results = {result}")
    
    print("\n2. PARALLELISM (CPU bound tasks with multiprocessing):")
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(cpu_intensive_task, 1_000_000) for _ in range(4)]
        results = [f.result() for f in futures]
    print(f"   Completed 4 CPU tasks in {time.time() - start:.2f}s")
    print(f"results = {results}")
    print("لاحظ أن زمن تنفيذ اربع عمليات معالجة باستخدام التوازي استغرق نفس زمن تنفيذ عملية واحدة تقريباً أو أقل")
    print("نفذ المثال التالي (رقم 4) لتعرف سبب التسريع في التنفيذ وفق قانون أمدال")

demonstrate_parallelism()
