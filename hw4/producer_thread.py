import threading
import queue
import time
import random

# Checklist: Use a tiny buffer (capacity 1 or 2)
BUFFER_SIZE = 2
buffer_queue = queue.Queue(maxsize=BUFFER_SIZE)

# Checklist: Run with 1 and 1 first, then change these to 3 and 3
NUM_PRODUCERS = 3  
NUM_CONSUMERS = 3  
ITEMS_PER_PRODUCER = 5

def producer(producer_id, items_to_produce):
    for i in range(items_to_produce):
        item = f"Data-{producer_id}-{i}"
        buffer_queue.put(item)  # Blocks safely if full
        print(f"[producer {producer_id}] produced item {i} \t buffer size: {buffer_queue.qsize()}")
        time.sleep(random.uniform(0.1, 0.3))

def consumer(consumer_id):
    while True:
        item = buffer_queue.get()  # Blocks safely if empty
        if item is None:
            print(f"[consumer {consumer_id}] received stop signal - exiting")
            buffer_queue.task_done()
            break
        print(f"[consumer {consumer_id}] consumed item \t buffer size: {buffer_queue.qsize()}")
        buffer_queue.task_done()
        time.sleep(random.uniform(0.2, 0.4))

if __name__ == "__main__":
    producers = []
    consumers = []

    # Dynamically create producers
    for i in range(1, NUM_PRODUCERS + 1):
        p = threading.Thread(target=producer, args=(i, ITEMS_PER_PRODUCER))
        producers.append(p)

    # Dynamically create consumers
    for i in range(1, NUM_CONSUMERS + 1):
        c = threading.Thread(target=consumer, args=(i,))
        consumers.append(c)

    # Start all threads
    for p in producers:
        p.start()
    for c in consumers:
        c.start()

    # Wait for producers to finish
    for p in producers:
        p.join()
    print("all producers finished")

    # Send a stop signal (None) for each consumer
    for _ in range(NUM_CONSUMERS):
        buffer_queue.put(None)

    # Wait for consumers to finish
    for c in consumers:
        c.join()
    print("all consumers finished, 0 items left")
