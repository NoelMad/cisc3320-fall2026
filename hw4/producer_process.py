import multiprocessing
import time
import random

def producer(buffer_queue, producer_id, items_to_produce):
    for i in range(items_to_produce):
        item = f"Data-{producer_id}-{i}"
        buffer_queue.put(item)  # Atomic & thread-safe: blocks safely if full
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
    BUFFER_SIZE = 5
    buffer_queue = multiprocessing.Queue(maxsize=BUFFER_SIZE)

    p1 = multiprocessing.Process(target=producer, args=(buffer_queue, 1, 5))
    p2 = multiprocessing.Process(target=producer, args=(buffer_queue, 2, 5))
    c1 = multiprocessing.Process(target=consumer, args=(buffer_queue, 1))
    c2 = multiprocessing.Process(target=consumer, args=(buffer_queue, 2))

    p1.start(); p2.start(); c1.start(); c2.start()

    p1.join(); p2.join()
    print("all producers finished")

    buffer_queue.put(None)
    buffer_queue.put(None)

    c1.join(); c2.join()
    print("all consumers finished, 0 items left")
