# race_condition_data_structure.py
import threading
import time
import random

def modify_list(shared_list, thread_id, num_operations):
    """Modify a shared list without synchronization"""
    for i in range(num_operations):
        # Operation 1: Append
        shared_list.append(f"Thread{thread_id}_Item{i}")
        
        # Small delay to increase race condition probability
        time.sleep(0.0001)
        
        # Operation 2: Sometimes remove an item
        if len(shared_list) > 10 and i % 3 == 0:
            # This can cause IndexError if another thread removes items
            try:
                shared_list.pop(random.randint(0, len(shared_list)-1))
            except IndexError:
                print(f"Thread {thread_id}: IndexError at iteration {i}!")
        
        # Operation 3: Modify existing items
        if len(shared_list) > 5:
            for j in range(min(3, len(shared_list))):
                try:
                    # Multiple threads might try to modify same index
                    shared_list[j] = f"Modified_by_Thread{thread_id}"
                except IndexError:
                    pass

def data_structure_race():
    """Demonstrate race condition with shared data structure"""
    print("=== DATA STRUCTURE RACE CONDITION ===")
    
    shared_list = []
    num_threads = 5
    operations_per_thread = 100
    
    print(f"Starting with empty list")
    print(f"Threads: {num_threads}, Operations per thread: {operations_per_thread}")
    
    threads = []
    errors = []
    
    # Error handler
    def thread_with_error_handling(thread_id):
        try:
            modify_list(shared_list, thread_id, operations_per_thread)
        except Exception as e:
            errors.append((thread_id, str(e)))
            print(f"Thread {thread_id} crashed with: {e}")
    
    # Create threads
    for i in range(num_threads):
        thread = threading.Thread(
            target=thread_with_error_handling,
            args=(i,),
            name=f"ListModifier-{i}"
        )
        threads.append(thread)
    
    # Start threads
    for thread in threads:
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    print(f"\nFinal list length: {len(shared_list)}")
    print(f"Expected max length: {num_threads * operations_per_thread}")
    
    if errors:
        print(f"\n⚠️  RACE CONDITIONS DETECTED: {len(errors)} threads crashed")
        for thread_id, error in errors:
            print(f"  Thread {thread_id}: {error}")
    else:
        print("\n✅ No crashes (got lucky with timing)")
    
    # Show some list contents
    print(f"\nSample items from list (first 10):")
    for item in shared_list[:10]:
        print(f"  {item}")
    
    return len(errors) > 0 


data_structure_race()
