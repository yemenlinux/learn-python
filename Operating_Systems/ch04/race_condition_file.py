# race_condition_file.py
import threading
import time
import os

def append_to_file(filename, thread_id, num_writes):
    """Append data to a file - prone to race condition"""
    for i in range(num_writes):
        # Read current content
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            content = ""
        
        # Modify content
        new_line = f"Thread {thread_id}, Write {i+1}\n"
        new_content = content + new_line
        
        # Simulate context switch opportunity
        time.sleep(0.001)
        
        # Write back
        with open(filename, 'w') as f:
            f.write(new_content)
        
        # Small delay
        time.sleep(0.0005)

def file_race_condition():
    """Demonstrate race condition in file operations"""
    print("=== FILE RACE CONDITION ===")
    
    filename = "race_condition_output.txt"
    
    # Clean up any existing file
    if os.path.exists(filename):
        os.remove(filename)
    
    num_threads = 5
    writes_per_thread = 10
    
    print(f"Creating file: {filename}")
    print(f"Threads: {num_threads}, Writes per thread: {writes_per_thread}")
    print(f"Expected lines in file: {num_threads * writes_per_thread}")
    
    # Create threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(
            target=append_to_file,
            args=(filename, i, writes_per_thread),
            name=f"FileWriter-{i}"
        )
        threads.append(thread)
    
    # Start threads
    for thread in threads:
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Read and analyze the file
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    print(f"\nActual lines in file: {len(lines)}")
    
    # Count lines by thread
    thread_counts = {}
    for line in lines:
        if line.startswith("Thread"):
            thread_id = line.split(",")[0].split()[1]
            thread_counts[thread_id] = thread_counts.get(thread_id, 0) + 1
    
    print("\nLines written by each thread:")
    for thread_id in sorted(thread_counts.keys()):
        print(f"  Thread {thread_id}: {thread_counts[thread_id]} lines")
    
    # Check for missing writes
    missing_writes = (num_threads * writes_per_thread) - len(lines)
    if missing_writes > 0:
        print(f"\n⚠️  RACE CONDITION DETECTED! {missing_writes} writes were lost.")
        print("   Multiple threads overwrote each other's changes.")
    else:
        print("\n✅ All writes completed successfully (got lucky with timing).")
    
    # Clean up
    if os.path.exists(filename):
        os.remove(filename)
    
    return len(lines)

def atomic_file_operations():
    """Show how to fix file race condition with locking"""
    print("\n=== FIXING FILE RACE CONDITION WITH LOCKING ===")
    
    import threading
    
    filename = "atomic_output.txt"
    lock = threading.Lock()
    
    def atomic_append(filename, thread_id, num_writes, lock):
        """Thread-safe file appending"""
        for i in range(num_writes):
            # Acquire lock before file operation
            with lock:
                try:
                    with open(filename, 'r') as f:
                        content = f.read()
                except FileNotFoundError:
                    content = ""
                
                new_line = f"Thread {thread_id}, Write {i+1}\n"
                new_content = content + new_line
                
                with open(filename, 'w') as f:
                    f.write(new_content)
    
    # Clean up
    if os.path.exists(filename):
        os.remove(filename)
    
    num_threads = 5
    writes_per_thread = 10
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(
            target=atomic_append,
            args=(filename, i, writes_per_thread, lock),
            name=f"AtomicWriter-{i}"
        )
        threads.append(thread)
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Check results
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    print(f"Lines written with locking: {len(lines)}")
    print(f"Expected: {num_threads * writes_per_thread}")
    
    if len(lines) == num_threads * writes_per_thread:
        print("✅ No race condition with proper locking!")
    
    # Clean up
    if os.path.exists(filename):
        os.remove(filename) 


file_race_condition()
atomic_file_operations()
