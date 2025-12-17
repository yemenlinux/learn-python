# race_condition_demo.py
import threading
import time
import random

from race_condition_bank import bank_race_condition
from race_condition_counter import counter_race_condition
from race_condition_file import file_race_condition
from race_condition_producer_consumer import producer_consumer_race
from race_condition_data_structure import data_structure_race


class RaceConditionDemonstrator:
    """Comprehensive race condition demonstration"""
    
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()
        self.counter_with_lock = 0
    
    def unsafe_increment(self, iterations=1000):
        """Increment without synchronization"""
        for _ in range(iterations):
            # Read
            current = self.counter
            # Context switch opportunity
            time.sleep(0.000001)
            # Write
            self.counter = current + 1
    
    def safe_increment(self, iterations=1000):
        """Increment with synchronization"""
        for _ in range(iterations):
            with self.lock:
                current = self.counter_with_lock
                time.sleep(0.000001)
                self.counter_with_lock = current + 1
    
    def run_comparison(self, num_threads=10, iterations=1000):
        """Compare safe vs unsafe incrementing"""
        print(f"{'='*70}")
        print(f"RACE CONDITION DEMONSTRATION")
        print(f"{'='*70}")
        print(f"Threads: {num_threads}, Increments per thread: {iterations}")
        print(f"Total increments attempted: {num_threads * iterations}")
        print()
        
        # Reset counters
        self.counter = 0
        self.counter_with_lock = 0
        
        # Create threads for unsafe increment
        unsafe_threads = []
        for i in range(num_threads):
            thread = threading.Thread(
                target=self.unsafe_increment,
                args=(iterations,),
                name=f"Unsafe-{i}"
            )
            unsafe_threads.append(thread)
        
        # Create threads for safe increment
        safe_threads = []
        for i in range(num_threads):
            thread = threading.Thread(
                target=self.safe_increment,
                args=(iterations,),
                name=f"Safe-{i}"
            )
            safe_threads.append(thread)
        
        # Run unsafe threads
        print("Running UNSAFE threads (no synchronization)...")
        start = time.time()
        
        for thread in unsafe_threads:
            thread.start()
        
        for thread in unsafe_threads:
            thread.join()
        
        unsafe_time = time.time() - start
        unsafe_result = self.counter
        print(f"  Unsafe counter: {unsafe_result}")
        print(f"  Time: {unsafe_time:.3f}s")
        
        # Run safe threads
        print("\nRunning SAFE threads (with lock)...")
        start = time.time()
        
        for thread in safe_threads:
            thread.start()
        
        for thread in safe_threads:
            thread.join()
        
        safe_time = time.time() - start
        safe_result = self.counter_with_lock
        
        print(f"  Safe counter: {safe_result}")
        print(f"  Time: {safe_time:.3f}s")
        
        # Results
        print(f"\n{'='*70}")
        print("RESULTS:")
        print(f"{'='*70}")
        expected = num_threads * iterations
        
        print(f"Expected counter value: {expected}")
        print()
        
        # Unsafe results
        if unsafe_result == expected:
            print(f"UNSAFE: ✅ Correct ({unsafe_result}) - got lucky!")
        else:
            lost = expected - unsafe_result
            percentage = (lost / expected) * 100
            print(f"UNSAFE: ⚠️  Incorrect ({unsafe_result})")
            print(f"        Lost {lost} increments ({percentage:.1f}%) due to race condition!")
        
        # Safe results
        if safe_result == expected:
            print(f"SAFE:   ✅ Correct ({safe_result})")
        else:
            print(f"SAFE:   ❌ Incorrect ({safe_result}) - something went wrong")
        
        # Performance comparison
        print(f"\nPerformance impact:")
        print(f"  Lock overhead: {safe_time - unsafe_time:.3f}s slower")
        
        return unsafe_result, safe_result

def demonstrate_all_race_conditions():
    """Run all race condition demonstrations"""
    print("RACE CONDITION DEMONSTRATION SUITE")
    print("=" * 70)
    
    # Get the demos from imported modules
    demos = [
        ("Bank Account Race", bank_race_condition),
        ("Counter Race", counter_race_condition),
        ("File Race", file_race_condition),
        ("Producer-Consumer Race", producer_consumer_race),
        ("Data Structure Race", data_structure_race),
    ]
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*70}")
        print(f"DEMO: {demo_name}")
        print(f"{'='*70}")
        
        try:
            result = demo_func()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error in {demo_name}: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            demonstrate_all_race_conditions()
        elif sys.argv[1] == "bank":
            bank_race_condition()
        elif sys.argv[1] == "counter":
            counter_race_condition()
        elif sys.argv[1] == "file":
            file_race_condition()
        elif sys.argv[1] == "producer":
            producer_consumer_race()
        elif sys.argv[1] == "data":
            data_structure_race()
        elif sys.argv[1] == "compare":
            demo = RaceConditionDemonstrator()
            demo.run_comparison(num_threads=20, iterations=1000)
        else:
            print("Usage: python race_condition_demo.py [all|bank|counter|file|producer|data|compare]")
    else:
        # Default: run the comparison demo
        demo = RaceConditionDemonstrator()
        demo.run_comparison() 
