import threading

lock = threading.Lock()

# This will return True if lock is acquired, If already blocked by other process it will return False.
lock.acquire(blocking=False)


# Below is same as blocking=True, if already acquired by other process, it will wait until it gets freed.
lock.acquire()