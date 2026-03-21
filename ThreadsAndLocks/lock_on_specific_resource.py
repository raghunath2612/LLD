import threading
from collections import defaultdict

locks = [threading.Lock() for i in range(10)]  # Creates a lock object for each value of i

def process(val):
    with locks[val]:
        """
        Here loc is acquired on val. first 1, 3, 5, 2 will execute parallel.
        Then 1 will execute.
        Then 1 will execute as 1 is present 3 times.
        And only one thing with same val can enter inside.
        """
        for i in range(100000000):
            if i % 10000000 == 0:
                print(val, i)
        print(f"Locked {val}")

def normal_process():
    values = [1, 3, 5, 1, 2, 1]
    threads = []
    for v in values:
        t = threading.Thread(target=process, args=(v,))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

normal_process()

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# For acquiring lock of an object with no prior info.
locks = defaultdict(threading.Lock)
def process_with_random_object(val):
    with locks[val]:
        print(f"Locked {val}")



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""
In high concurrent systems two process can get lock on same value at the same time.
Like in our example of array [1, 3, 5, 1, 2, 1],
if all the 3 ones are called at one time, there is a possibility that all three can enter the with block at same time.
To overcome this, below is the alternative approach.
"""

locks = {}
global_lock = threading.Lock()
def get_lock(val):
    """
    When process3 wants to run for same 1 value at the same time,
    it will call come here. But global_lock will only allow one.
    When the second process enters, it only gets the lock after the first one got.
    By the time second process wants to run process3, by the time first process already acquires lock.
    """
    with global_lock:
        if val not in locks:
            locks[val] = threading.Lock()
        return locks[val]

def process3(val):
    lock = get_lock(val)
    with lock:
        print("Do anything you want")