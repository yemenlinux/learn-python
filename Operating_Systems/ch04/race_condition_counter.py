# race_condition_counter.py
import threading
import time

def increment_counter(counter, num_increments, delay=0):
    """Increment counter many times - prone to race condition"""
    for _ in range(num_increments):
        # Read current value
        current = counter['value']
        
        # Simulate some work (increases chance of race condition)
        if delay > 0:
            time.sleep(delay)
        
        # Write new value
        counter['value'] = current + 1

def counter_race_condition():
    """Demonstrate simple counter race condition"""
    print("=== COUNTER RACE CONDITION ===")
    
    # Shared counter (using dict so it's mutable)
    counter = {'value': 0}
    num_threads = 10
    increments_per_thread = 1000
    
    print(f"Starting counter: {counter['value']}")
    print(f"Threads: {num_threads}, Increments per thread: {increments_per_thread}")
    print(f"Expected final value: {num_threads * increments_per_thread}")
    
    # Create and start threads
    threads = []
    for i in range(num_threads):
        # Add small random delay to increase race condition probability
        delay = 0.00001 * (i % 3)
        thread = threading.Thread(
            target=increment_counter,
            args=(counter, increments_per_thread, delay),
            name=f"Incrementer-{i}"
        )
        threads.append(thread)
    
    start_time = time.time()
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    elapsed_time = time.time() - start_time
    
    print(f"\nFinal counter: {counter['value']}")
    print(f"Expected: {num_threads * increments_per_thread}")
    print(f"Difference: {num_threads * increments_per_thread - counter['value']}")
    print(f"Time elapsed: {elapsed_time:.3f} seconds")
    
    if counter['value'] != num_threads * increments_per_thread:
        print("\n⚠️  RACE CONDITION DETECTED! Counter is incorrect.")
        print(f"   Lost {num_threads * increments_per_thread - counter['value']} increments.")
    else:
        print("\n✅ Counter is correct (got lucky with timing).")
    
    return counter['value']

def visualize_race_condition():
    """Visualize how race conditions happen step by step"""
    print("\n=== VISUALIZING RACE CONDITION ===")
    print("Imagine two threads (A and B) both incrementing a counter from 0:")
    print()
    print("Thread A:                     Thread B:")
    print("1. Read counter (0)           (idle)")
    print("2. Increment to 1             (idle)")
    print("3. (Context switch!)          1. Read counter (still 0!)")
    print("4. (paused)                   2. Increment to 1")
    print("5. Write 1 to counter         3. Write 1 to counter")
    print()
    print("RESULT: Counter is 1, but should be 2!")
    print("Both threads read 0, incremented to 1, and wrote 1.")
    print("One increment was lost!") 

counter_race_condition()
visualize_race_condition()
