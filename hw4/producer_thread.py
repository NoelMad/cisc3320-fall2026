import threading
import queue
import time
import random

BUFFER_SIZE = 5
buffer_queue = queue.Queue(maxsize=BUFFER_SIZE)

def producer(producer_id, items_to_produce):
    for i in range(items_to_produce):
        item = f"Data-{producer_id}-{i}"
        buffer_queue.put(item)  # Blocks if buffer is full
        print(f"[Thread-Producer {producer_id}] Produced: {item} (Queue size: {buffer_queue.qsize()})")
        time.sleep(random.uniform(0.1, 0.3))

def consumer(consumer_id, items_to_consume):
    for _ in range(items_to_consume):
        item = buffer_queue.get()  # Blocks if buffer is empty
        print(f"[Thread-Consumer {consumer_id}] Consumed: {item}")
        buffer_queue.task_done()
        time.sleep(random.uniform(0.2, 0.4))

if __name__ == "__main__":
    # 2 producers, 2 consumers, each handling 5 items
    p1 = threading.Thread(target=producer, args=(1, 5))
    p2 = threading.Thread(target=producer, args=(2, 5))
    c1 = threading.Thread(target=consumer, args=(1, 5))
    c2 = threading.Thread(target=consumer, args=(2, 5))

    p1.start(); p2.start(); c1.start(); c2.start()
    p1.join(); p2.join(); c1.join(); c2.join()
    print("Threading producer-consumer finished.")
