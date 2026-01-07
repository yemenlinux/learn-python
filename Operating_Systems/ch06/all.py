"""
Chapter 6: Synchronization Tools - Python Demonstrations
Operating System Concepts - 10th Edition
Silberschatz, Galvin and Gagne ©2018
"""

import threading
import time
import random
from queue import Queue
import sys

# ============================================================================
# 1. RACE CONDITION DEMONSTRATION
# ============================================================================

def demonstrate_race_condition():
    """
    Demonstrates how concurrent access to shared data without synchronization
    leads to data inconsistency (race condition).
    """
    print("=" * 60)
    print("1. RACE CONDITION DEMONSTRATION")
    print("=" * 60)
    
    class Counter:
        def __init__(self):
            self.value = 0  # Shared resource
    
    def increment_counter(counter, num_increments, thread_name):
        for _ in range(num_increments):
            current_value = counter.value
            # Simulating context switch by sleeping
            time.sleep(0.001)  # Small delay to increase chance of race condition
            counter.value = current_value + 1
        print(f"{thread_name}: Finished. Final counter value from thread's perspective: {counter.value}")
    
    # Create shared counter
    counter = Counter()
    
    # Create two threads that will increment the counter
    thread1 = threading.Thread(target=increment_counter, args=(counter, 100, "Thread-1"))
    thread2 = threading.Thread(target=increment_counter, args=(counter, 100, "Thread-2"))
    
    print("Starting two threads that each increment a shared counter 100 times...")
    print("Expected final value: 200")
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    print(f"\nActual final counter value: {counter.value}")
    print(f"Lost updates: {200 - counter.value}")
    print("This is a RACE CONDITION!\n")

# ============================================================================
# 2. PETERSON'S SOLUTION (for two processes/threads)
# ============================================================================

def demonstrate_peterson_solution():
    """
    Implements Peterson's algorithm for mutual exclusion between two threads.
    Note: This is a demonstration; real implementation needs memory barriers.
    """
    print("=" * 60)
    print("2. PETERSON'S SOLUTION")
    print("=" * 60)
    
    # Shared variables for Peterson's algorithm
    flag = [False, False]  # Indicates intention to enter critical section
    turn = 0  # Indicates whose turn it is
    
    class PetersonLock:
        def __init__(self, thread_id):
            self.thread_id = thread_id
            self.other = 1 if thread_id == 0 else 0
        
        def acquire(self):
            flag[self.thread_id] = True  # I want to enter
            turn = self.other  # You go first
            # Wait while other wants to enter and it's their turn
            while flag[self.other] and turn == self.other:
                pass  # Busy wait (spinlock)
        
        def release(self):
            flag[self.thread_id] = False  # I'm done
    
    # Shared resource
    critical_section_counter = 0
    
    def critical_section_task(thread_id, lock, iterations=5):
        nonlocal critical_section_counter
        for i in range(iterations):
            lock.acquire()
            # CRITICAL SECTION
            print(f"Thread-{thread_id} entered critical section")
            temp = critical_section_counter
            time.sleep(0.01)  # Simulate work
            critical_section_counter = temp + 1
            print(f"Thread-{thread_id} exiting critical section, counter = {critical_section_counter}")
            lock.release()
            time.sleep(0.05)  # Remainder section
    
    # Create locks for two threads
    lock0 = PetersonLock(0)
    lock1 = PetersonLock(1)
    
    # Create threads
    t1 = threading.Thread(target=critical_section_task, args=(0, lock0))
    t2 = threading.Thread(target=critical_section_task, args=(1, lock1))
    
    print("Peterson's Algorithm for two threads:")
    print("- flag[2]: Indicates if a thread wants to enter")
    print("- turn: Indicates whose turn it is")
    print("- Provides mutual exclusion, progress, and bounded waiting\n")
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    print(f"\nFinal counter value: {critical_section_counter} (should be 10)")
    print("Note: In real systems, Peterson's solution needs memory barriers!\n")

# ============================================================================
# 3. HARDWARE SUPPORT: TEST-AND-SET & COMPARE-AND-SWAP
# ============================================================================

def demonstrate_hardware_instructions():
    """
    Simulates hardware synchronization primitives using Python's atomic operations.
    In real hardware, these are implemented as single, uninterruptible instructions.
    """
    print("=" * 60)
    print("3. HARDWARE SUPPORT FOR SYNCHRONIZATION")
    print("=" * 60)
    
    # Simulating test-and-set instruction
    print("A. TEST-AND-SET Instruction Simulation")
    print("- Atomic operation that sets a value to True and returns old value")
    
    def test_and_set(target):
        """Simulates test-and-set atomic instruction"""
        old_value = target[0]
        target[0] = True
        return old_value
    
    # Using test-and-set to implement a lock
    lock = [False]  # Shared lock variable
    
    def critical_section_with_tas(thread_id, iterations=3):
        for i in range(iterations):
            # Acquire lock using test-and-set
            while test_and_set(lock):
                pass  # Busy wait (spinlock)
            
            # CRITICAL SECTION
            print(f"Thread-{thread_id} in critical section (iteration {i+1})")
            time.sleep(0.1)
            
            # Release lock
            lock[0] = False
    
    print("\nB. COMPARE-AND-SWAP Instruction Simulation")
    print("- Atomic operation that compares and swaps if expected value matches")
    
    def compare_and_swap(target, expected, new_value):
        """Simulates compare-and-swap atomic instruction"""
        old_value = target[0]
        if old_value == expected:
            target[0] = new_value
        return old_value
    
    # Using compare-and-swap to implement a lock
    cas_lock = [0]  # 0 = unlocked, 1 = locked
    
    def critical_section_with_cas(thread_id, iterations=3):
        for i in range(iterations):
            # Acquire lock using compare-and-swap
            while compare_and_swap(cas_lock, 0, 1) != 0:
                pass  # Busy wait
            
            # CRITICAL SECTION
            print(f"Thread-{thread_id} in critical section using CAS (iteration {i+1})")
            time.sleep(0.1)
            
            # Release lock
            cas_lock[0] = 0
    
    print("\nThese hardware instructions form the basis for many synchronization primitives.")
    print("In Python, we simulate them, but in hardware they're single, atomic instructions.\n")

# ============================================================================
# 4. MUTEX LOCKS (MUTUAL EXCLUSION LOCKS)
# ============================================================================

def demonstrate_mutex_locks():
    """
    Demonstrates mutex locks using Python's threading.Lock.
    Shows both correct usage and potential deadlock scenarios.
    """
    print("=" * 60)
    print("4. MUTEX LOCKS")
    print("=" * 60)
    
    print("A. CORRECT USAGE OF MUTEX LOCKS")
    
    shared_counter = 0
    counter_lock = threading.Lock()
    
    def increment_with_lock(thread_name, increments=50):
        nonlocal shared_counter
        for i in range(increments):
            counter_lock.acquire()  # ENTRY SECTION
            try:
                # CRITICAL SECTION
                current = shared_counter
                time.sleep(0.001)  # Simulate work
                shared_counter = current + 1
            finally:
                counter_lock.release()  # EXIT SECTION
            # REMAINDER SECTION
            time.sleep(0.005)
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=increment_with_lock, args=(f"Thread-{i}",))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"Final counter value with mutex: {shared_counter} (expected: 250)")
    
    print("\nB. DEADLOCK EXAMPLE WITH MUTEX LOCKS")
    
    lock_a = threading.Lock()
    lock_b = threading.Lock()
    
    def process_1():
        """Acquires lock_a then lock_b"""
        lock_a.acquire()
        print("Process 1 acquired lock A")
        time.sleep(0.1)  # Simulate work
        
        lock_b.acquire()  # This will wait forever if process_2 has lock_b
        print("Process 1 acquired lock B")
        
        # Critical section
        time.sleep(0.1)
        
        lock_b.release()
        lock_a.release()
        print("Process 1 released both locks")
    
    def process_2():
        """Acquires lock_b then lock_a (OPPOSITE ORDER = DEADLOCK!)"""
        lock_b.acquire()
        print("Process 2 acquired lock B")
        time.sleep(0.1)  # Simulate work
        
        lock_a.acquire()  # This will wait forever if process_1 has lock_a
        print("Process 2 acquired lock A")
        
        # Critical section
        time.sleep(0.1)
        
        lock_a.release()
        lock_b.release()
        print("Process 2 released both locks")
    
    # Uncomment to see deadlock (will hang)
    # print("Creating deadlock scenario (commented out to prevent hanging)...")
    # t1 = threading.Thread(target=process_1)
    # t2 = threading.Thread(target=process_2)
    # t1.start()
    # t2.start()
    # t1.join(timeout=2)
    # t2.join(timeout=2)
    # print("If you see this after timeout, deadlock was prevented by timeout.")
    
    print("\nC. MUTEX WITH TIMEOUT (DEADLOCK PREVENTION)")
    
    def process_with_timeout(process_id, first_lock, second_lock, timeout=1):
        """Tries to acquire locks with timeout to prevent deadlock"""
        # Try to acquire first lock with timeout
        if not first_lock.acquire(timeout=timeout):
            print(f"Process {process_id}: Failed to acquire first lock (timeout)")
            return
        
        print(f"Process {process_id}: Acquired first lock")
        time.sleep(0.05)
        
        # Try to acquire second lock with timeout
        if not second_lock.acquire(timeout=timeout):
            print(f"Process {process_id}: Failed to acquire second lock, releasing first")
            first_lock.release()
            return
        
        print(f"Process {process_id}: Acquired both locks")
        time.sleep(0.1)  # Critical section
        
        second_lock.release()
        first_lock.release()
        print(f"Process {process_id}: Released both locks")
    
    print("\nMutex locks provide mutual exclusion but require careful use to avoid deadlocks.\n")

# ============================================================================
# 5. SEMAPHORES
# ============================================================================

def demonstrate_semaphores():
    """
    Demonstrates counting semaphores and binary semaphores (mutex).
    Shows how semaphores can be used for synchronization beyond mutual exclusion.
    """
    print("=" * 60)
    print("5. SEMAPHORES")
    print("=" * 60)
    
    print("A. BINARY SEMAPHORE (MUTEX EQUIVALENT)")
    
    # Binary semaphore (value 0 or 1) - same as mutex
    binary_semaphore = threading.Semaphore(1)  # Initial value = 1 (available)
    
    shared_resource = 0
    
    def task_with_binary_sem(thread_id, iterations=3):
        for i in range(iterations):
            binary_semaphore.acquire()  # wait() or P() operation
            
            # CRITICAL SECTION
            print(f"Thread-{thread_id} entered critical section")
            nonlocal shared_resource
            temp = shared_resource
            time.sleep(0.05)
            shared_resource = temp + 1
            print(f"Thread-{thread_id} exiting, resource = {shared_resource}")
            
            binary_semaphore.release()  # signal() or V() operation
            time.sleep(0.1)  # Remainder section
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=task_with_binary_sem, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"\nFinal shared resource value: {shared_resource} (should be 9)")
    
    print("\nB. COUNTING SEMAPHORE (LIMITED RESOURCE ACCESS)")
    
    # Counting semaphore - allows up to 3 concurrent accesses
    counting_semaphore = threading.Semaphore(3)
    concurrent_counter = 0
    max_concurrent = 0
    
    def access_limited_resource(thread_id):
        nonlocal concurrent_counter, max_concurrent
        
        print(f"Thread-{thread_id} waiting to access resource...")
        counting_semaphore.acquire()
        
        # Track concurrent accesses
        concurrent_counter += 1
        if concurrent_counter > max_concurrent:
            max_concurrent = concurrent_counter
        
        print(f"Thread-{thread_id} accessing resource (concurrent: {concurrent_counter})")
        time.sleep(random.uniform(0.1, 0.3))
        print(f"Thread-{thread_id} releasing resource")
        
        concurrent_counter -= 1
        counting_semaphore.release()
    
    print("\nStarting 10 threads with semaphore allowing only 3 concurrent accesses...")
    threads = []
    for i in range(10):
        t = threading.Thread(target=access_limited_resource, args=(i,))
        threads.append(t)
        t.start()
        time.sleep(0.05)
    
    for t in threads:
        t.join()
    
    print(f"Maximum concurrent accesses: {max_concurrent} (should be 3 or less)")
    
    print("\nC. SEMAPHORE FOR SEQUENCING (S1 BEFORE S2)")
    
    # Semaphore for sequencing - ensure task1 completes before task2 starts
    synch_semaphore = threading.Semaphore(0)  # Initial value = 0
    
    def task1():
        print("Task 1: Starting S1...")
        time.sleep(0.2)
        print("Task 1: Finished S1")
        synch_semaphore.release()  # Signal that S1 is done
    
    def task2():
        print("Task 2: Waiting for S1 to complete...")
        synch_semaphore.acquire()  # Wait for S1
        print("Task 2: Starting S2...")
        time.sleep(0.1)
        print("Task 2: Finished S2")
    
    t1 = threading.Thread(target=task1)
    t2 = threading.Thread(target=task2)
    
    t2.start()  # Start task2 first - it will wait
    time.sleep(0.1)
    t1.start()  # Then start task1
    
    t1.join()
    t2.join()
    
    print("\nSemaphores are more flexible than mutexes and can solve various synchronization problems.\n")

# ============================================================================
# 6. MONITORS AND CONDITION VARIABLES
# ============================================================================

def demonstrate_monitors():
    """
    Demonstrates monitors using Python's threading.Condition.
    Shows how monitors encapsulate shared data and synchronization.
    """
    print("=" * 60)
    print("6. MONITORS AND CONDITION VARIABLES")
    print("=" * 60)
    
    print("A. BASIC MONITOR WITH CONDITION VARIABLE")
    
    # Implementing a bounded buffer (producer-consumer) using monitor
    class BoundedBuffer:
        """Monitor implementation of bounded buffer"""
        def __init__(self, capacity):
            self.capacity = capacity
            self.buffer = Queue(maxsize=capacity)
            self.condition = threading.Condition()
        
        def produce(self, item):
            with self.condition:
                # Wait while buffer is full
                while self.buffer.full():
                    print(f"Producer waiting, buffer full ({self.buffer.qsize()}/{self.capacity})")
                    self.condition.wait()
                
                # Add item to buffer
                self.buffer.put(item)
                print(f"Produced: {item}, buffer size: {self.buffer.qsize()}/{self.capacity}")
                
                # Notify consumers
                self.condition.notify_all()
        
        def consume(self):
            with self.condition:
                # Wait while buffer is empty
                while self.buffer.empty():
                    print("Consumer waiting, buffer empty")
                    self.condition.wait()
                
                # Remove item from buffer
                item = self.buffer.get()
                print(f"Consumed: {item}, buffer size: {self.buffer.qsize()}/{self.capacity}")
                
                # Notify producers
                self.condition.notify_all()
                return item
    
    # Test the bounded buffer
    buffer = BoundedBuffer(3)
    
    def producer(producer_id, num_items=5):
        for i in range(num_items):
            item = f"Item-{producer_id}-{i}"
            buffer.produce(item)
            time.sleep(random.uniform(0.1, 0.3))
    
    def consumer(consumer_id, num_items=5):
        for i in range(num_items):
            item = buffer.consume()
            time.sleep(random.uniform(0.15, 0.35))
    
    print("\nStarting producer-consumer with monitor (bounded buffer size: 3)...")
    prod1 = threading.Thread(target=producer, args=(1, 5))
    prod2 = threading.Thread(target=producer, args=(2, 5))
    cons1 = threading.Thread(target=consumer, args=(1, 5))
    cons2 = threading.Thread(target=consumer, args=(2, 5))
    
    cons1.start()
    cons2.start()
    prod1.start()
    prod2.start()
    
    prod1.join()
    prod2.join()
    cons1.join()
    cons2.join()
    
    print("\nB. CONDITION VARIABLE FOR ORDERING (S1 BEFORE S2)")
    
    class OrderingMonitor:
        """Monitor to ensure S1 executes before S2"""
        def __init__(self):
            self.condition = threading.Condition()
            self.s1_done = False
        
        def execute_s1(self):
            with self.condition:
                print("S1: Starting...")
                time.sleep(0.2)
                print("S1: Finished")
                self.s1_done = True
                self.condition.notify_all()
        
        def execute_s2(self):
            with self.condition:
                while not self.s1_done:
                    print("S2: Waiting for S1 to complete...")
                    self.condition.wait()
                print("S2: Starting...")
                time.sleep(0.1)
                print("S2: Finished")
    
    ordering_monitor = OrderingMonitor()
    
    t_s2 = threading.Thread(target=ordering_monitor.execute_s2)
    t_s1 = threading.Thread(target=ordering_monitor.execute_s1)
    
    t_s2.start()
    time.sleep(0.1)  # Ensure S2 starts first and waits
    t_s1.start()
    
    t_s1.join()
    t_s2.join()
    
    print("\nMonitors provide higher-level abstraction and simplify concurrent programming.\n")

# ============================================================================
# 7. LIVENESS ISSUES
# ============================================================================

def demonstrate_liveness_issues():
    """
    Demonstrates liveness problems: deadlock, starvation, and priority inversion.
    """
    print("=" * 60)
    print("7. LIVENESS ISSUES")
    print("=" * 60)
    
    print("A. DEADLOCK (Circular Wait)")
    
    # Classic deadlock with four conditions:
    # 1. Mutual Exclusion
    # 2. Hold and Wait
    # 3. No Preemption
    # 4. Circular Wait
    
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    lock3 = threading.Lock()
    
    def deadlock_task1():
        lock1.acquire()
        print("Task1 acquired Lock1")
        time.sleep(0.1)
        lock2.acquire()
        print("Task1 acquired Lock2")
        lock2.release()
        lock1.release()
    
    def deadlock_task2():
        lock2.acquire()
        print("Task2 acquired Lock2")
        time.sleep(0.1)
        lock3.acquire()
        print("Task2 acquired Lock3")
        lock3.release()
        lock2.release()
    
    def deadlock_task3():
        lock3.acquire()
        print("Task3 acquired Lock3")
        time.sleep(0.1)
        lock1.acquire()  # This creates circular wait: T1->L1, T2->L2, T3->L3, T3->L1
        print("Task3 acquired Lock1")
        lock1.release()
        lock3.release()
    
    print("Deadlock scenario with 3 threads and 3 locks (circular wait)...")
    print("Thread1: Lock1 → Lock2")
    print("Thread2: Lock2 → Lock3")
    print("Thread3: Lock3 → Lock1")
    print("\nThis creates a circular wait (deadlock).")
    
    # Uncomment to see deadlock
    # t1 = threading.Thread(target=deadlock_task1)
    # t2 = threading.Thread(target=deadlock_task2)
    # t3 = threading.Thread(target=deadlock_task3)
    # t1.start(); t2.start(); t3.start()
    # t1.join(timeout=2); t2.join(timeout=2); t3.join(timeout=2)
    
    print("\nB. STARVATION")
    
    # Starvation: a thread never gets CPU time/resources
    high_priority_done = False
    
    def high_priority_task():
        nonlocal high_priority_done
        for i in range(10):
            print(f"High priority task working... {i+1}/10")
            time.sleep(0.05)
        high_priority_done = True
    
    def low_priority_task():
        attempts = 0
        while not high_priority_done and attempts < 20:
            print("Low priority task waiting...")
            time.sleep(0.1)
            attempts += 1
        if high_priority_done:
            print("Low priority task finally running!")
        else:
            print("Low priority task STARVED (gave up waiting)")
    
    print("\nSimulating starvation: low-priority task may never run...")
    t_low = threading.Thread(target=low_priority_task, name="LowPriority")
    t_high = threading.Thread(target=high_priority_task, name="HighPriority")
    
    t_low.start()
    time.sleep(0.05)  # Let low priority start first
    t_high.start()
    
    t_high.join()
    t_low.join()
    
    print("\nC. PRIORITY INVERSION")
    
    # Priority inversion: low-priority task holds lock needed by high-priority task
    shared_lock = threading.Lock()
    medium_done = threading.Event()
    
    def low_priority():
        print("Low-priority task started")
        shared_lock.acquire()
        print("Low-priority task acquired lock")
        time.sleep(0.5)  # Holds lock for a while
        print("Low-priority task releasing lock")
        shared_lock.release()
    
    def medium_priority():
        print("Medium-priority task started")
        medium_done.set()  # Signal that medium task is running
        time.sleep(1)
        print("Medium-priority task finished")
    
    def high_priority():
        print("High-priority task started, waiting for lock...")
        medium_done.wait()  # Wait to ensure medium task runs
        shared_lock.acquire()
        print("High-priority task finally got lock")
        shared_lock.release()
        print("High-priority task finished")
    
    print("\nPriority inversion scenario:")
    print("1. Low-priority task acquires lock")
    print("2. High-priority task needs same lock (blocks)")
    print("3. Medium-priority task runs (blocks low-priority)")
    print("4. High-priority task waits for medium which waits for low - PRIORITY INVERSION!")
    
    t_low = threading.Thread(target=low_priority, name="LowPriority")
    t_medium = threading.Thread(target=medium_priority, name="MediumPriority")
    t_high = threading.Thread(target=high_priority, name="HighPriority")
    
    t_low.start()
    time.sleep(0.1)  # Ensure low gets lock first
    t_high.start()
    time.sleep(0.1)  # Ensure high starts and blocks
    t_medium.start()
    
    t_low.join()
    t_medium.join()
    t_high.join()
    
    print("\nLiveness failures prevent systems from making progress.\n")

# ============================================================================
# 8. SYNCHRONIZATION TOOLS EVALUATION
# ============================================================================

def evaluate_synchronization_tools():
    """
    Evaluates different synchronization tools and their characteristics.
    """
    print("=" * 60)
    print("8. SYNCHRONIZATION TOOLS EVALUATION")
    print("=" * 60)
    
    tools = [
        {
            "name": "Peterson's Solution",
            "description": "Software-based for 2 processes",
            "advantages": ["Simple, elegant", "No hardware support needed"],
            "disadvantages": ["Not scalable beyond 2 processes", "Needs memory barriers on modern CPUs"],
            "best_for": "Educational purposes, simple 2-thread scenarios"
        },
        {
            "name": "Test-and-Set / Compare-and-Swap",
            "description": "Hardware atomic instructions",
            "advantages": ["Very fast", "Efficient for low contention"],
            "disadvantages": ["Busy waiting (spinlocks)", "Hardware-dependent"],
            "best_for": "Low-level OS implementation, short critical sections"
        },
        {
            "name": "Mutex Locks",
            "description": "Software locks for mutual exclusion",
            "advantages": ["Widely supported", "Simple API", "No busy waiting (blocking)"],
            "disadvantages": ["Can cause deadlock", "Overhead for context switching"],
            "best_for": "General-purpose mutual exclusion"
        },
        {
            "name": "Semaphores",
            "description": "Integer-based synchronization",
            "advantages": ["More flexible than mutexes", "Can control multiple resources", "Useful for signaling"],
            "disadvantages": ["More complex to use correctly", "Prone to subtle bugs"],
            "best_for": "Resource pools, producer-consumer, complex synchronization"
        },
        {
            "name": "Monitors",
            "description": "High-level synchronization construct",
            "advantages": ["Encapsulates synchronization", "Higher-level abstraction", "Reduces errors"],
            "disadvantages": ["Less flexible than semaphores", "Language support varies"],
            "best_for": "Object-oriented concurrent programming"
        }
    ]
    
    print("SUMMARY OF SYNCHRONIZATION TOOLS")
    print("-" * 60)
    
    for i, tool in enumerate(tools, 1):
        print(f"\n{i}. {tool['name']}")
        print(f"   Description: {tool['description']}")
        print(f"   Advantages: {', '.join(tool['advantages'])}")
        print(f"   Disadvantages: {', '.join(tool['disadvantages'])}")
        print(f"   Best for: {tool['best_for']}")
    
    print("\n" + "=" * 60)
    print("GUIDELINES FOR CHOOSING SYNCHRONIZATION TOOLS")
    print("=" * 60)
    print("""
    1. For simple mutual exclusion → Use Mutex Locks
    2. For controlling access to multiple resources → Use Counting Semaphores
    3. For signaling between threads → Use Condition Variables (in Monitors)
    4. For OS/kernel development → Use Hardware Atomic Instructions
    5. For high-level application code → Use Monitors with Condition Variables
    6. For maximum performance in low-contention scenarios → Use Spinlocks
    7. For educational understanding → Study Peterson's Algorithm
    """)

# ============================================================================
# 9. PRACTICAL EXAMPLE: DINING PHILOSOPHERS PROBLEM
# ============================================================================

def dining_philosophers():
    """
    Classic synchronization problem demonstrating deadlock and solutions.
    """
    print("=" * 60)
    print("9. DINING PHILOSOPHERS PROBLEM")
    print("=" * 60)
    
    print("Problem: 5 philosophers, 5 chopsticks, need 2 chopsticks to eat")
    print("Potential for deadlock if all pick up left chopstick first")
    
    class Philosopher(threading.Thread):
        def __init__(self, name, left_chopstick, right_chopstick):
            threading.Thread.__init__(self)
            self.name = name
            self.left_chopstick = left_chopstick
            self.right_chopstick = right_chopstick
        
        def run(self):
            for i in range(3):  # Each philosopher eats 3 times
                self.think()
                self.eat(i)
        
        def think(self):
            print(f"{self.name} is thinking...")
            time.sleep(random.uniform(0.1, 0.3))
        
        def eat(self, meal_number):
            # Try to acquire chopsticks
            print(f"{self.name} is hungry for meal #{meal_number+1}")
            
            # SOLUTION 1: Resource hierarchy (always pick up lower-numbered chopstick first)
            # This prevents circular wait
            first = min(self.left_chopstick, self.right_chopstick, key=id)
            second = max(self.left_chopstick, self.right_chopstick, key=id)
            
            with first:
                print(f"{self.name} picked up first chopstick")
                time.sleep(0.1)  # Makes deadlock more likely if not using hierarchy
                with second:
                    print(f"{self.name} picked up second chopstick and is EATING")
                    time.sleep(random.uniform(0.2, 0.4))
                    print(f"{self.name} finished eating")
            
            # Alternative solutions:
            # 1. Allow only 4 philosophers to eat at once (semaphore with count 4)
            # 2. Require philosopher to pick up both chopsticks atomically
            # 3. Use a waiter/monitor to coordinate
    
    # Create chopsticks (locks)
    chopsticks = [threading.Lock() for _ in range(5)]
    
    # Create philosophers
    philosophers = [
        Philosopher(f"Philosopher-{i}", 
                   chopsticks[i], 
                   chopsticks[(i + 1) % 5])
        for i in range(5)
    ]
    
    print("\nStarting dining philosophers with resource hierarchy solution...")
    for p in philosophers:
        p.start()
    
    for p in philosophers:
        p.join()
    
    print("\nAll philosophers have finished dining (no deadlock)!")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("OPERATING SYSTEM CONCEPTS - CHAPTER 6: SYNCHRONIZATION TOOLS")
    print("Python Implementation Demonstrations")
    print("=" * 70 + "\n")
    
    # Ask user which demonstrations to run
    print("Available Demonstrations:")
    print("1. Race Condition")
    print("2. Peterson's Solution")
    print("3. Hardware Support (Test-and-Set, Compare-and-Swap)")
    print("4. Mutex Locks")
    print("5. Semaphores")
    print("6. Monitors and Condition Variables")
    print("7. Liveness Issues (Deadlock, Starvation, Priority Inversion)")
    print("8. Synchronization Tools Evaluation")
    print("9. Dining Philosophers Problem")
    print("A. Run ALL demonstrations")
    print("Q. Quit")
    
    choice = input("\nEnter your choice (1-9, A, or Q): ").upper()
    
    if choice == 'Q':
        print("Exiting...")
        return
    
    demonstrations = {
        '1': demonstrate_race_condition,
        '2': demonstrate_peterson_solution,
        '3': demonstrate_hardware_instructions,
        '4': demonstrate_mutex_locks,
        '5': demonstrate_semaphores,
        '6': demonstrate_monitors,
        '7': demonstrate_liveness_issues,
        '8': evaluate_synchronization_tools,
        '9': dining_philosophers,
    }
    
    if choice == 'A':
        # Run all demonstrations
        for key in sorted(demonstrations.keys()):
            demonstrations[key]()
            input("\nPress Enter to continue to next demonstration...\n")
    elif choice in demonstrations:
        demonstrations[choice]()
    else:
        print("Invalid choice!")
    
    print("\n" + "=" * 70)
    print("END OF CHAPTER 6 DEMONSTRATIONS")
    print("=" * 70)

if __name__ == "__main__":
    main() 
