import multiprocessing
import time
import random

def producer(buffer_queue, producer_id, items_to_produce):
    for i in range(items_to_produce):
        item = f"Data-{producer_id}-{i}"
        buffer_queue.put(item)  # Blocks safely if full
        print(f"[producer {producer_id}] produced item {i} \t buffer size: {buffer_queue.qsize()}")
        time.sleep(random.uniform(0.1, 0.3))

def consumer(buffer_queue, consumer_id):
    while True:
        item = buffer_queue.get()  # Blocks safely if empty
        if item is None:
            print(f"[consumer {consumer_id}] received stop signal - exiting")
            break
        print(f"[consumer {consumer_id}] consumed item \t buffer size: {buffer_queue.qsize()}")
        time.sleep(random.uniform(0.2, 0.4))

if __name__ == "__main__":
    # Checklist: Use a tiny buffer (capacity 1 or 2)
    BUFFER_SIZE = 2
    buffer_queue = multiprocessing.Queue(maxsize=BUFFER_SIZE)

    # Checklist: Run with 1 and 1 first, then change these to 3 and 3
    NUM_PRODUCERS = 3  
    NUM_CONSUMERS = 3  
    ITEMS_PER_PRODUCER = 5

    producers = []
    consumers = []

    # Dynamically create processes
    for i in range(1, NUM_PRODUCERS + 1):
        p = multiprocessing.Process(target=producer, args=(buffer_queue, i, ITEMS_PER_PRODUCER))
        producers.append(p)

    for i in range(1, NUM_CONSUMERS + 1):
        c = multiprocessing.Process(target=consumer, args=(buffer_queue, i))
        consumers.append(c)

    # Start all processes
    for p in producers:
        p.start()
    for c in consumers:
        c.start()

    # Wait for producers to finish
    for p in producers:
        p.join()
    print("all producers finished")

    # Send a stop signal for each consumer
    for _ in range(NUM_CONSUMERS):
        buffer_queue.put(None)

    # Wait for consumers to finish
    for c in consumers:
        c.join()
    print("all consumers finished, 0 items left")
