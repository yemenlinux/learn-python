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
print("THREADS & CONCURRENCY IN PYTHON")
print("=" * 60)

# ============================================================================
# SLIDES 1-4: INTRODUCTION & MOTIVATION
# ============================================================================
print("\n" + "="*60)
print("SLIDES 1-4: Introduction & Motivation for Threads")
print("="*60)

print("""
KEY CONCEPTS:
- Threads are lightweight processes within a program
- Multiple threads can run concurrently within same process
- Threads share memory space, making communication easier than processes
- Modern applications (web servers, GUI apps) heavily use threads
""")

def motivation_example():
    """Demonstrates why we need threads (like Slide 5's Word Processor example)"""
    print("\nExample: Multi-threaded Application (like Word Processor):")
    print("- Thread 1: Accept user input")
    print("- Thread 2: Auto-save document")
    print("- Thread 3: Check spelling in background")
    print("- Thread 4: Update UI display")
    print("\nAll these can happen concurrently!")

motivation_example()

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
    
    
    
    print("\n1. CONCURRENCY (I/O bound tasks with threading):")
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(io_bound_task, i) for i in range(4)]
        results = [f.result() for f in futures]
    print(f"   Completed 4 I/O tasks in {time.time() - start:.2f}s")
    
    print("\n2. PARALLELISM (CPU bound tasks with multiprocessing):")
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(cpu_intensive_task, 1000000) for _ in range(4)]
        results = [f.result() for f in futures]
    print(f"   Completed 4 CPU tasks in {time.time() - start:.2f}s")

demonstrate_parallelism()

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
        time.sleep(0.1 * work_units)
    
    # Single core
    start = time.time()
    serial_portion()
    parallelizable_portion(1)
    single_time = time.time() - start
    
    # Four cores (theoretically)
    start = time.time()
    serial_portion()
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Divide work among 4 threads
        futures = [executor.submit(parallelizable_portion, 0.25) for _ in range(4)]
        for f in futures:
            f.result()
    multi_time = time.time() - start
    
    print(f"\nSingle core time: {single_time:.2f}s")
    print(f"Four cores time: {multi_time:.2f}s")
    print(f"Actual speedup: {single_time/multi_time:.2f}x")

amdahls_law_demo()

# ============================================================================
# SLIDES 17-20: USER THREADS VS KERNEL THREADS
# ============================================================================
print("\n" + "="*60)
print("SLIDES 17-20: User Threads vs Kernel Threads")
print("="*60)

shared_counter = 0
lock = Lock()

def increment_counter(n):
    global shared_counter
    for _ in range(n):
        with lock:  # Need lock due to GIL
            shared_counter += 1

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
    
    # Demonstrate the difference
    print("\nDemonstration: GIL limitation in Python threads")
    
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
        t = Thread(target=increment_counter, args=(100000,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    thread_time = time.time() - start
    print(f"Threads completed in {thread_time:.2f}s, Counter: {shared_counter}")
    
    # Using processes (kernel-level)
    def increment_process(n, return_dict, pid):
        local_counter = 0
        for _ in range(n):
            local_counter += 1
        return_dict[pid] = local_counter
    
    start = time.time()
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []
    
    for i in range(4):
        p = multiprocessing.Process(target=increment_process, 
                                   args=(100000, return_dict, i))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    process_total = sum(return_dict.values())
    process_time = time.time() - start
    print(f"Processes completed in {process_time:.2f}s, Total: {process_total}")

user_vs_kernel_threads()

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
    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(handle_request, i, "Process") for i in range(5)]
        for future in concurrent.futures.as_completed(futures):
            print(f"  {future.result()}")

threading_models_demo()

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

# ============================================================================
# SLIDES 57-64: THREADING ISSUES
# ============================================================================
print("\n" + "="*60)
print("SLIDES 57-64: Threading Issues")
print("="*60)

def threading_issues_demo():
    """
    Common threading issues:
    - Race conditions
    - Deadlocks
    - Thread cancellation
    - Thread-local storage
    """
    
    print("\n1. Race Conditions and Locks:")
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
    # Thread(target=worker1).start()
    # Thread(target=worker2).start()
    print("  (Deadlock example skipped to avoid hanging)")
    print("  Solution: Always acquire locks in same order!")
    
    print("\n3. Thread-Local Storage (TLS):")
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
    print("-" * 50)
    
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
    
    worker = CancellableWorker()
    print("Starting worker thread...")
    worker.start()
    time.sleep(2)
    print("Stopping worker thread...")
    worker.stop()

threading_issues_demo()

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

# ============================================================================
# COMPREHENSIVE EXAMPLE: MULTI-THREADED SERVER
# ============================================================================
print("\n" + "="*60)
print("COMPREHENSIVE EXAMPLE: Multi-threaded Server")
print("(Combines concepts from multiple slides)")
print("="*60)

class ThreadedServerSimulation:
    """
    Simulates a multi-threaded server architecture (Slide 6)
    with thread pool, task queue, and graceful shutdown
    """
    
    def __init__(self, num_workers=3):
        self.task_queue = queue.Queue()
        self.workers = []
        self.shutdown_flag = False
        self.num_workers = num_workers
        self.lock = Lock()
        self.completed_tasks = 0
        
        # Create worker threads
        for i in range(num_workers):
            worker = Thread(target=self._worker_loop, name=f"Worker-{i}")
            worker.daemon = True
            self.workers.append(worker)
    
    def start(self):
        print(f"Starting server with {self.num_workers} worker threads...")
        for worker in self.workers:
            worker.start()
    
    def submit_task(self, task_id, duration):
        """Client submits a task (Slide 6 step 1)"""
        self.task_queue.put((task_id, duration))
        print(f"Task {task_id} submitted to queue")
    
    def _worker_loop(self):
        """Worker thread processing tasks (Slide 6 step 2)"""
        worker_name = threading.current_thread().name
        
        while not self.shutdown_flag:
            try:
                # Get task with timeout to check shutdown flag
                task_id, duration = self.task_queue.get(timeout=0.5)
                
                print(f"{worker_name} processing task {task_id}...")
                time.sleep(duration)  # Simulate work
                
                with self.lock:
                    self.completed_tasks += 1
                
                print(f"{worker_name} completed task {task_id}")
                self.task_queue.task_done()
                
            except queue.Empty:
                continue  # Check shutdown flag and continue
    
    def wait_for_completion(self):
        """Wait for all tasks to complete"""
        self.task_queue.join()
    
    def shutdown(self):
        """Graceful shutdown"""
        print("\nInitiating graceful shutdown...")
        self.shutdown_flag = True
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=1.0)
        
        print(f"Server shutdown complete. Tasks completed: {self.completed_tasks}")

# Run the server simulation
print("\nSimulating Multi-threaded Server Architecture:")
print("-" * 50)

server = ThreadedServerSimulation(num_workers=3)
server.start()

# Simulate client requests
for i in range(10):
    duration = random.uniform(0.5, 2.0)
    server.submit_task(i, duration)
    time.sleep(0.2)  # Simulate time between requests

# Wait for tasks to complete
server.wait_for_completion()
server.shutdown()

print("\n" + "="*60)
print("KEY PYTHON MODULES COVERED:")
print("="*60)
print("""
1. threading        - Basic thread operations
2. multiprocessing  - True parallelism with processes
3. concurrent.futures - High-level async execution
4. queue            - Thread-safe queues for task distribution
5. threading.Lock   - Mutual exclusion for critical sections
6. threading.local  - Thread-local storage
7. threading.Event  - Thread communication and cancellation
""")

print("\n" + "="*60)
print("PYTHON-SPECIFIC NOTES:")
print("="*60)
print("""
- Python has GIL (Global Interpreter Lock) limiting CPU parallelism with threads
- Use threading for I/O-bound tasks, multiprocessing for CPU-bound tasks
- concurrent.futures provides high-level interface for both
- Always use locks for shared mutable state
- Consider thread pools (ThreadPoolExecutor) over manual thread creation
- Python abstracts OS differences in threading API
""")

print("\n" + "="*60)
print("END OF THREADS & CONCURRENCY DEMONSTRATION")
print("="*60)
