import threading

def count_numbers_with_out_lock():
    global count_with_out_lock
    for _ in range(10000):
        count_with_out_lock += 1
        # print(f"Incremented by one: {count_with_out_lock}")

def count_numbers_with_locking():
    lock = threading.Lock()
    global count_with_lock
    for _ in range(10000):
        with lock:
            count_with_lock += 1

def with_out_lock_example():
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=count_numbers_with_out_lock)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join() # without join the main thread will exit before all the threads finisher

def with_lock_example():
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=count_numbers_with_locking)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    count_with_out_lock = 0
    count_with_lock = 0
    with_out_lock_example()
    with_lock_example()
    print(f"count with out lock: {count_with_out_lock}")
    print(f"count with lock: {count_with_lock}")
    """ Here because of GIL (Global Interpreter Lock) in python, a block of code can be run by a single thread
            at a time. In other languages both counts should return different outputs.
    """
