import threading
import time

process1_count = 0
process2_count = 0

def process1():
    while True:
        global process1_count
        print(f"In Process 1: {process1_count}")
        process1_count += 1
        # time.sleep(0.5)


def process2():
    while True:
        global process2_count
        print(f"In Process 2: {process2_count}")
        process2_count += 1
        # time.sleep(0.5)


t1 = threading.Thread(target=process1)
t2 = threading.Thread(target=process2)
t1.start()
t2.start()
t1.join()
t2.join()