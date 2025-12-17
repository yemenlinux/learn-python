# race_condition_producer_consumer.py
import threading
import time
import random
from collections import deque

class UnsafeBuffer:
    """Buffer without proper synchronization - prone to race conditions"""
    def __init__(self, capacity=10):
        self.buffer = deque(maxlen=capacity)
        self.counter = 0  # Shared counter with race condition
    
    def produce(self, producer_id):
        """Produce an item - not thread-safe"""
        if len(self.buffer) < self.buffer.maxlen:
            # Read-modify-write race condition
            time.sleep(random.uniform(0.001, 0.005))  # Context switch opportunity
            
            # Critical section: multiple producers can produce simultaneously
            item = f"Item {self.counter} from Producer {producer_id}"
            self.buffer.append(item)
            
            # Increment counter (race condition here!)
            current = self.counter
            time.sleep(0.001)  # Context switch opportunity
            self.counter = current + 1
            
            print(f"Producer {producer_id} produced: {item}")
            return True
        else:
            print(f"Producer {producer_id}: Buffer full!")
            return False
    
    def consume(self, consumer_id):
        """Consume an item - not thread-safe"""
        if len(self.buffer) > 0:
            # Read-modify race condition
            time.sleep(random.uniform(0.001, 0.005))  # Context switch opportunity
            
            # Critical section: multiple consumers can try to consume same item
            if len(self.buffer) > 0:  # Double-check (still not safe!)
                item = self.buffer.popleft()
                print(f"Consumer {consumer_id} consumed: {item}")
                return True
        
        print(f"Consumer {consumer_id}: Buffer empty!")
        return False

def producer_task(buffer, producer_id, num_items):
    """Producer thread function"""
    for i in range(num_items):
        buffer.produce(producer_id)
        time.sleep(random.uniform(0.01, 0.05))

def consumer_task(buffer, consumer_id, num_items):
    """Consumer thread function"""
    for i in range(num_items):
        buffer.consume(consumer_id)
        time.sleep(random.uniform(0.01, 0.05))

def producer_consumer_race():
    """Demonstrate producer-consumer race condition"""
    print("=== PRODUCER-CONSUMER RACE CONDITION ===")
    
    buffer = UnsafeBuffer(capacity=5)
    
    # Create producers and consumers
    producers = []
    consumers = []
    
    num_producers = 3
    num_consumers = 2
    items_per_producer = 20
    
    # Create producer threads
    for i in range(num_producers):
        producer = threading.Thread(
            target=producer_task,
            args=(buffer, i, items_per_producer),
            name=f"Producer-{i}"
        )
        producers.append(producer)
    
    # Create consumer threads
    for i in range(num_consumers):
        consumer = threading.Thread(
            target=consumer_task,
            args=(buffer, i, items_per_producer),
            name=f"Consumer-{i}"
        )
        consumers.append(consumer)
    
    # Start all threads
    all_threads = producers + consumers
    
    print(f"Starting {len(producers)} producers and {len(consumers)} consumers")
    print(f"Each producer creates {items_per_producer} items")
    print()
    
    start_time = time.time()
    
    for thread in all_threads:
        thread.start()
    
    # Wait for completion
    for thread in all_threads:
        thread.join()
    
    elapsed_time = time.time() - start_time
    
    print(f"\nFinal counter value: {buffer.counter}")
    print(f"Expected counter: {num_producers * items_per_producer}")
    print(f"Buffer items remaining: {len(buffer.buffer)}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    
    # Check for race conditions
    issues_found = False
    
    # Check 1: Counter should equal total produced items
    if buffer.counter != num_producers * items_per_producer:
        print(f"\n⚠️  RACE CONDITION 1: Counter is {buffer.counter}, expected {num_producers * items_per_producer}")
        print(f"   Lost {num_producers * items_per_producer - buffer.counter} increments")
        issues_found = True
    
    # Check 2: Some items might have been lost or duplicated
    print("\nItems in buffer at end:")
    for item in buffer.buffer:
        print(f"  {item}")
    
    return issues_found 


producer_consumer_race()
