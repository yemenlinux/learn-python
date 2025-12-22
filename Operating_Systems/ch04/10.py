import threading
import concurrent.futures
import time
from queue import Queue
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ThreadType(Enum):
    """Types of threads in our two-level model"""
    BOUND = "BOUND"      # Bound to specific kernel thread (1:1)
    MULTIPLEXED = "MUX"  # Multiplexed on pool (M:M)

@dataclass
class Task:
    """Represents a task to be executed"""
    id: int
    priority: int  # 1 = highest, 5 = lowest
    thread_type: ThreadType
    duration: float

class TwoLevelThreadManager:
    """
    Simulates a two-level threading model
    
    Features:
    - Bound threads: Critical tasks get dedicated threads
    - Multiplexed threads: Regular tasks share thread pool
    """
    
    def __init__(self, num_bound_threads: int = 2, num_pool_threads: int = 4):
        self.num_bound_threads = num_bound_threads
        self.num_pool_threads = num_pool_threads
        
        # Create dedicated threads for bound tasks
        self.bound_threads = {}
        self.bound_thread_available = {}
        
        for i in range(num_bound_threads):
            thread_name = f"Bound-Thread-{i}"
            self.bound_threads[thread_name] = None  # No task initially
            self.bound_thread_available[thread_name] = True
        
        # Create thread pool for multiplexed tasks
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=num_pool_threads,
            thread_name_prefix="Mux-Thread"
        )
        
        # Queue for tasks waiting for bound threads
        self.bound_task_queue = Queue()
        
        print(f"Two-Level Thread Manager Initialized:")
        print(f"  - Bound threads (1:1): {num_bound_threads}")
        print(f"  - Multiplexed pool (M:M): {num_pool_threads} threads")
        print("-" * 50)
    
    def execute_task(self, task: Task):
        """Execute task based on its type"""
        if task.thread_type == ThreadType.BOUND:
            return self._execute_bound_task(task)
        else:
            return self._execute_multiplexed_task(task)
    
    def _execute_bound_task(self, task: Task):
        """Execute on dedicated bound thread"""
        print(f"[BOUND] Task {task.id} (Priority: {task.priority}) - "
              f"Requesting dedicated thread...")
        
        # Try to find available bound thread
        thread_name = None
        for name, available in self.bound_thread_available.items():
            if available:
                thread_name = name
                self.bound_thread_available[name] = False
                self.bound_threads[name] = task
                break
        
        if thread_name is None:
            print(f"[BOUND] Task {task.id} - All bound threads busy, queuing...")
            # In real system, this might block or queue
            # For simulation, we'll wait for a thread
            time.sleep(0.5)  # Simulate waiting
            thread_name = list(self.bound_threads.keys())[0]
        
        # Execute task on bound thread
        print(f"[BOUND] Task {task.id} - Running on {thread_name}")
        time.sleep(task.duration)
        
        # Mark thread as available
        self.bound_thread_available[thread_name] = True
        self.bound_threads[thread_name] = None
        
        result = f"Task {task.id} completed on {thread_name}"
        return result
    
    def _execute_multiplexed_task(self, task: Task):
        """Execute on multiplexed thread pool"""
        print(f"[MUX] Task {task.id} (Priority: {task.priority}) - "
              f"Submitting to thread pool...")
        
        future = self.thread_pool.submit(self._run_multiplexed_task, task)
        return future.result()
    
    def _run_multiplexed_task(self, task: Task):
        """Actual task execution for multiplexed tasks"""
        thread_name = threading.current_thread().name
        print(f"[MUX] Task {task.id} - Running on {thread_name} "
              f"(shared with other tasks)")
        time.sleep(task.duration)
        return f"Task {task.id} completed on shared {thread_name}"
    
    def shutdown(self):
        """Clean shutdown"""
        self.thread_pool.shutdown(wait=True)
        print("\nTwo-Level Thread Manager shutdown complete")

def simulate_real_world_scenario():
    """
    Simulate a real-world scenario where two-level threading is useful:
    - Database connections (bound threads for transactions)
    - Web requests (multiplexed for concurrency)
    - Background tasks (multiplexed)
    """
    
    print("\n" + "="*60)
    print("REAL-WORLD SCENARIO: Web Server with Two-Level Threading")
    print("="*60)
    
    # Initialize our two-level thread manager
    manager = TwoLevelThreadManager(
        num_bound_threads=2,      # For critical operations
        num_pool_threads=5        # For regular requests
    )
    
    # Create various tasks with different requirements
    tasks = [
        # Critical tasks that need dedicated threads (bound)
        Task(101, 1, ThreadType.BOUND, 2.0),    # Payment processing
        Task(102, 1, ThreadType.BOUND, 1.5),    # Database transaction
        Task(103, 2, ThreadType.BOUND, 1.0),    # Order confirmation
        
        # Regular tasks that can be multiplexed
        Task(201, 3, ThreadType.MULTIPLEXED, 0.5),  # Product search
        Task(202, 3, ThreadType.MULTIPLEXED, 0.3),  # User login
        Task(203, 4, ThreadType.MULTIPLEXED, 0.7),  # Image loading
        Task(204, 4, ThreadType.MULTIPLEXED, 0.2),  # API call
        Task(205, 5, ThreadType.MULTIPLEXED, 0.4),  # Logging
        Task(206, 5, ThreadType.MULTIPLEXED, 0.6),  # Analytics
    ]
    
    print("\nStarting task execution with two-level model:")
    print("- Critical tasks use BOUND threads (dedicated)")
    print("- Regular tasks use MULTIPLEXED threads (shared pool)")
    print("-" * 50)
    
    # Execute all tasks
    results = []
    start_time = time.time()
    
    for task in tasks:
        result = manager.execute_task(task)
        results.append(result)
    
    # Simulate additional bound tasks arriving later
    print("\n" + "="*50)
    print("SIMULATION: New critical task arrives")
    print("="*50)
    
    # This shows bound threads can handle new critical tasks
    emergency_task = Task(999, 1, ThreadType.BOUND, 0.8)  # Emergency backup
    emergency_result = manager.execute_task(emergency_task)
    results.append(emergency_result)
    
    total_time = time.time() - start_time
    
    print("\n" + "="*50)
    print("RESULTS SUMMARY")
    print("="*50)
    
    # Show which threads handled which tasks
    bound_thread_work = {}
    mux_thread_work = {}
    
    for result in results:
        if "Bound-Thread" in result:
            thread = result.split("on ")[1]
            bound_thread_work[thread] = bound_thread_work.get(thread, 0) + 1
        elif "Mux-Thread" in result:
            thread = result.split("on ")[1]
            mux_thread_work[thread] = mux_thread_work.get(thread, 0) + 1
    
    print("\nBound Threads Work Distribution (1:1 model):")
    for thread, count in bound_thread_work.items():
        print(f"  {thread}: {count} critical tasks")
    
    print("\nMultiplexed Threads Work Distribution (M:M model):")
    for thread, count in mux_thread_work.items():
        print(f"  {thread}: {count} regular tasks")
    
    print(f"\nTotal execution time: {total_time:.2f} seconds")
    
    manager.shutdown()
    
    return results

# Advanced Example: Simulating OS-Level Two-Level Model
def os_level_simulation():
    """
    Simulates how an OS might implement two-level threads
    with Lightweight Processes (LWPs)
    """
    
    print("\n" + "="*60)
    print("OS-LEVEL SIMULATION: Two-Level Threads with LWPs")
    print("="*60)
    
    class LightweightProcess:
        """Simulates an LWP (bridge between user and kernel threads)"""
        def __init__(self, lwp_id):
            self.lwp_id = lwp_id
            self.user_thread = None
            self.kernel_thread = f"Kernel-Thread-{lwp_id}"
            self.busy = False
        
        def assign_thread(self, user_thread):
            self.user_thread = user_thread
            self.busy = True
            print(f"LWP-{self.lwp_id}: Assigned '{user_thread}' -> {self.kernel_thread}")
        
        def release(self):
            self.user_thread = None
            self.busy = False
    
    class TwoLevelOS:
        """Simulates OS with two-level threading"""
        def __init__(self, num_lwps=3):
            self.lwps = [LightweightProcess(i) for i in range(num_lwps)]
            self.user_threads = []
            self.thread_pool_size = 10  # Multiplexed threads
            
            print(f"\nOS Initialized with {num_lwps} LWPs")
            print("Each LWP connects user threads to kernel threads")
            print("-" * 50)
        
        def create_user_thread(self, name, requires_bound=False):
            """Create user thread with optional binding to LWP"""
            self.user_threads.append(name)
            
            if requires_bound:
                # Bind to available LWP (1:1 mapping)
                for lwp in self.lwps:
                    if not lwp.busy:
                        lwp.assign_thread(name)
                        return f"Thread '{name}' bound to LWP-{lwp.lwp_id}"
                return f"Thread '{name}' waiting for LWP (all busy)"
            else:
                # Multiplex on thread pool (M:M)
                return f"Thread '{name}' multiplexed on pool of {self.thread_pool_size} threads"
        
        def show_status(self):
            print("\nCurrent OS Threading Status:")
            print("-" * 40)
            print("LWPs (Lightweight Processes):")
            for lwp in self.lwps:
                status = f"Running '{lwp.user_thread}'" if lwp.busy else "Idle"
                print(f"  LWP-{lwp.lwp_id}: {status} -> {lwp.kernel_thread}")
            
            print(f"\nTotal User Threads: {len(self.user_threads)}")
            print(f"Thread Pool Size: {self.thread_pool_size}")
    
    # Simulate OS operations
    os = TwoLevelOS(num_lwps=2)
    
    # Create various threads
    print("\nCreating user threads:")
    print(os.create_user_thread("GUI-Main", requires_bound=True))
    print(os.create_user_thread("Audio-Processing", requires_bound=True))
    print(os.create_user_thread("Network-1", requires_bound=False))
    print(os.create_user_thread("Network-2", requires_bound=False))
    print(os.create_user_thread("File-IO", requires_bound=False))
    
    # Try to create another bound thread (should wait)
    print(os.create_user_thread("RealTime-Video", requires_bound=True))
    
    os.show_status()
    
    print("\n" + "="*50)
    print("KEY INSIGHTS:")
    print("="*50)
    print("1. BOUND THREADS (via LWP):")
    print("   - Get dedicated kernel thread")
    print("   - Better performance, priority scheduling")
    print("   - Used for: GUI, audio, real-time tasks")
    
    print("\n2. MULTIPLEXED THREADS:")
    print("   - Share kernel thread pool")
    print("   - Higher concurrency, less overhead")
    print("   - Used for: network I/O, file operations")
    
    print("\n3. HYBRID ADVANTAGE:")
    print("   - Critical tasks guaranteed resources")
    print("   - Regular tasks get good throughput")
    print("   - Flexible resource allocation")

# Run the examples
if __name__ == "__main__":
    # Example 1: Basic concept
    print("TWO-LEVEL THREADING MODEL EXPLANATION")
    print("="*60)
    print("""
    Two-level threading combines:
    1. M:M Model (Many-to-Many):
       - Multiple user threads → Multiple kernel threads
       - Efficient for regular tasks
       
    2. 1:1 Model (One-to-One):
       - One user thread → One kernel thread (bound)
       - Best for critical/real-time tasks
    """)
    
    # Example 2: Web server simulation
    results = simulate_real_world_scenario()
    
    # Example 3: OS-level simulation
    os_level_simulation()
    
    print("\n" + "="*60)
    print("WHY TWO-LEVEL THREADS ARE USEFUL:")
    print("="*60)
    print("""
    1. Performance Critical Applications:
       - Database systems bind transaction threads
       - Games bind rendering threads
       - Real-time systems bind control threads
       
    2. Resource Management:
       - Don't waste kernel threads on low-priority tasks
       - Reserve kernel threads for important work
       
    3. Flexibility:
       - Mix and match based on task requirements
       - Adapt to changing workload patterns
       
    4. Load Balancing:
       - OS can move multiplexed threads between cores
       - Bound threads stay on dedicated cores
    """)
