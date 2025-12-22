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
# SLIDES 23-27: MULTITHREADING MODELS
# ============================================================================
print("\n" + "="*60)
print("SLIDES 23-27: Multithreading Models")
print("="*60)

# Simulating the models with examples
print("\nPractical Example: Web Server with Different Models")

def handle_request(request_id, model):
    time.sleep(0.1)  # Simulate request processing
    return f"Request {request_id} handled by {model}"

def threading_models_demo():
    """
    Demonstrating different threading models conceptually
    Many-to-One, One-to-One, Many-to-Many, Two-level
    """
    
    print("\nThreading Models in Python Context:")
    print("-" * 50)
    
    print("\n1. Many-to-One (M:1):")
    print("   - Multiple user threads map to single kernel thread")
    print("   - Python's threading module with GIL behaves somewhat like this")
    print("   - Blocking I/O affects all threads")
    
    print("\n2. One-to-One (1:1):")
    print("   - Each user thread maps to a kernel thread")
    print("   - This is what multiprocessing achieves")
    print("   - True parallelism, more overhead")
    
    print("\n3. Many-to-Many (M:M):")
    print("   - Flexible mapping, can use multiple cores efficiently")
    print("   - Not directly supported in Python standard library")
    print("   - Some third-party libraries attempt this")
    
    print("\n4. Two-level Model:")
    print("   - Mix of M:M with some 1:1 bindings")
    print("   - Used in some JVM implementations")
    
    
    
    # Many-to-One simulation (threads compete for GIL)
    print("\nSimulating Many-to-One (Python threads with GIL):")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(handle_request, i, "Thread") for i in range(5)]
        for future in concurrent.futures.as_completed(futures):
            print(f"  {future.result()}")
    
    # One-to-One simulation (true parallelism)
    print("\nSimulating One-to-One (Multiprocessing):")
    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(handle_request, i, "Process") for i in range(5)]
        for future in concurrent.futures.as_completed(futures):
            print(f"  {future.result()}")

threading_models_demo()
