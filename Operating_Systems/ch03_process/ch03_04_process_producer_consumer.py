import multiprocessing
import time
import random

def producer(queue, items_to_produce):
    """Producer process - generates items"""
    for i in range(items_to_produce):
        item = f"Item-{i}"
        queue.put(item)
        print(f"Produced: {item}")
        time.sleep(random.uniform(0.1, 0.5))
    
    # Signal end of production
    queue.put(None)

def consumer(queue, consumer_id):
    """Consumer process - processes items"""
    while True:
        item = queue.get()
        if item is None:
            # Put it back for other consumers
            queue.put(None)
            break
        
        print(f"Consumer {consumer_id} consumed: {item}")
        time.sleep(random.uniform(0.2, 0.7))

def producer_consumer_demo():
    """Demonstrate producer-consumer pattern"""
    queue = multiprocessing.Queue(maxsize=5)  # Bounded buffer
    
    # Create producer
    producer_process = multiprocessing.Process(
        target=producer, 
        args=(queue, 10)
    )
    
    # Create consumers
    consumers = []
    for i in range(2):
        consumer_process = multiprocessing.Process(
            target=consumer, 
            args=(queue, i)
        )
        consumers.append(consumer_process)
    
    # Start all processes
    producer_process.start()
    for c in consumers:
        c.start()
    
    # Wait for completion
    producer_process.join()
    for c in consumers:
        c.join()
    
    print("Producer-Consumer completed")

producer_consumer_demo()
