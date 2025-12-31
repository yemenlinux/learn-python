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
# SLIDES 57-64: THREADING ISSUES
# ============================================================================
print("\n" + "="*60)
print("SLIDES 57-64: Threading Issues")
print("مشاكل الخيوط")
print("="*60)

# thread cancellation pattern
# see example number 4 in the threading_issues_demo
class CancellableWorker:
    def __init__(self):
        self._stop_event = threading.Event()
        self.thread = Thread(target=self._run)
    
    def start(self):
        self.thread.start()
    
    def stop(self):
        self._stop_event.set()
        self.thread.join()
    
    def _run(self):
        while not self._stop_event.is_set():
            print(f"  {threading.current_thread().name} working...")
            time.sleep(0.5)
        print(f"  {threading.current_thread().name} stopped gracefully")

def threading_issues_demo():
    """
    Common threading issues:
    - Race conditions
    - Deadlocks
    - Thread cancellation
    - Thread-local storage
    """
    
    print("\n1. Race Conditions and Locks:")
    print("حالات التسابق والأقفال")
    print("-" * 50)
    
    class BankAccount:
        def __init__(self, balance):
            self.balance = balance
            self.lock = Lock()
        
        def unsafe_withdraw(self, amount):
            # UNSAFE: No lock
            if self.balance >= amount:
                time.sleep(0.001)  # Simulate processing delay
                self.balance -= amount
                return True
            return False
        
        def safe_withdraw(self, amount):
            # SAFE: With lock
            with self.lock:
                if self.balance >= amount:
                    time.sleep(0.001)
                    self.balance -= amount
                    return True
            return False
    
    # Test unsafe version
    print("Testing UNSAFE withdrawal (race condition):")
    account = BankAccount(1000)
    
    def unsafe_withdraw_task():
        for _ in range(100):
            account.unsafe_withdraw(1)
    
    threads = [Thread(target=unsafe_withdraw_task) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    print(f"  Expected balance: 0, Actual: {account.balance}")
    
    # Test safe version
    print("\nTesting SAFE withdrawal (with lock):")
    account = BankAccount(1000)
    
    def safe_withdraw_task():
        for _ in range(100):
            account.safe_withdraw(1)
    
    threads = [Thread(target=safe_withdraw_task) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    print(f"  Expected balance: 0, Actual: {account.balance}")
    
    print("\n2. Deadlock Example:")
    print("مثال على القفلات (توقف النظام عن العمل")
    print("-" * 50)
    
    lock_a = Lock()
    lock_b = Lock()
    
    def worker1():
        with lock_a:
            print("Worker 1 acquired lock A")
            time.sleep(0.1)
            print("Worker 1 trying to acquire lock B...")
            with lock_b:  # This will deadlock if worker2 got lock B first
                print("Worker 1 acquired lock B")
    
    def worker2():
        with lock_b:
            print("Worker 2 acquired lock B")
            time.sleep(0.1)
            print("Worker 2 trying to acquire lock A...")
            with lock_a:  # This will deadlock if worker1 got lock A first
                print("Worker 2 acquired lock A")
    
    # To avoid deadlock, don't run this:
    # للتنفيذ قم بإزالة الكومنت من السطرين التاليين
    # Thread(target=worker1).start()
    # Thread(target=worker2).start()
    print("  (Deadlock example skipped to avoid hanging)")
    print("  Solution: Always acquire locks in same order!")
    
    print("\n3. Thread-Local Storage (TLS):")
    print("مشكلة التخزين المحلي")
    print("-" * 50)
    
    # Create thread-local storage
    thread_data = thread_local()
    
    def show_thread_local():
        # Each thread gets its own 'value' attribute
        if not hasattr(thread_data, 'value'):
            thread_data.value = 0
        
        thread_data.value += 1
        print(f"  Thread {threading.current_thread().name}: value = {thread_data.value}")
    
    threads = []
    for i in range(3):
        t = Thread(target=lambda: [show_thread_local() for _ in range(3)], 
                  name=f"Worker-{i}")
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("\n4. Thread Cancellation Pattern:")
    print("مشكلة ايقاف الثريد (الخيوط) عند الحاجة")
    print("-" * 50)
    
    
    worker = CancellableWorker()
    print("Starting worker thread...")
    worker.start()
    time.sleep(5)
    print("Stopping worker thread...")
    worker.stop()

threading_issues_demo()
