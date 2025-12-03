import multiprocessing
import time

def shared_memory_example():
    """Demonstrate shared memory between processes"""
    
    # Create shared value and array
    shared_value = multiprocessing.Value('i', 0)  # integer
    shared_array = multiprocessing.Array('i', 5)  # integer array of size 5
    
    def worker1(shared_val, shared_arr):
        """First worker process"""
        for i in range(5):
            with shared_val.get_lock():
                shared_val.value += 1
                print(f"Worker1: shared_value = {shared_val.value}")
            
            shared_arr[i] = i * 10
            time.sleep(0.5)
    
    def worker2(shared_val, shared_arr):
        """Second worker process"""
        for i in range(5):
            with shared_val.get_lock():
                shared_val.value += 10
                print(f"Worker2: shared_value = {shared_val.value}")
            
            time.sleep(0.3)
    
    # Create and start processes
    p1 = multiprocessing.Process(target=worker1, args=(shared_value, shared_array))
    p2 = multiprocessing.Process(target=worker2, args=(shared_value, shared_array))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    print(f"Final shared_value: {shared_value.value}")
    print(f"Final shared_array: {list(shared_array)}")

shared_memory_example()
