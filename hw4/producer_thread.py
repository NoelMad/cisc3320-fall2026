import threading
import queue
import time
import random

BUFFER_SIZE = 5
buffer_queue = queue.Queue(maxsize=BUFFER_SIZE)

def producer(producer_id, items_to_produce):
    for i in range(items_to_produce):
        item = f"Data-{producer_id}-{i}"
        buffer_queue.put(item)  # Atomic & thread-safe: blocks safely if full
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
    p1 = threading.Thread(target=producer, args=(1, 5))
    p2 = threading.Thread(target=producer, args=(2, 5))
    c1 = threading.Thread(target=consumer, args=(1,))
    c2 = threading.Thread(target=consumer, args=(2,))

    p1.start(); p2.start(); c1.start(); c2.start()

    p1.join(); p2.join()
    print("all producers finished")

    buffer_queue.put(None)
    buffer_queue.put(None)

    c1.join(); c2.join()
    print("all consumers finished, 0 items left")
