import multiprocessing
import time
import random

def producer(buffer_queue, producer_id, items_to_produce):
    for i in range(items_to_produce):
        item = f"Data-{producer_id}-{i}"
        buffer_queue.put(item)  # Blocks if buffer is full
        print(f"[Process-Producer {producer_id}] Produced: {item}")
        time.sleep(random.uniform(0.1, 0.3))

def consumer(buffer_queue, consumer_id, items_to_consume):
    for _ in range(items_to_consume):
        item = buffer_queue.get()  # Blocks if buffer is empty
        print(f"[Process-Consumer {consumer_id}] Consumed: {item}")
        time.sleep(random.uniform(0.2, 0.4))

if __name__ == "__main__":
    BUFFER_SIZE = 5
    buffer_queue = multiprocessing.Queue(maxsize=BUFFER_SIZE)

    # 2 producers, 2 consumers, each handling 5 items
    p1 = multiprocessing.Process(target=producer, args=(buffer_queue, 1, 5))
    p2 = multiprocessing.Process(target=producer, args=(buffer_queue, 2, 5))
    c1 = multiprocessing.Process(target=consumer, args=(buffer_queue, 1, 5))
    c2 = multiprocessing.Process(target=consumer, args=(buffer_queue, 2, 5))

    p1.start(); p2.start(); c1.start(); c2.start()
    p1.join(); p2.join(); c1.join(); c2.join()
    print("Multiprocessing producer-consumer finished.")
