from queue import Queue
from random import random
from threading import Event, Thread
from time import sleep

hb = Event()
hb.set()
q = Queue()


def worker():
    for i in range(5):
        hb.wait()
        hb.clear()  # clear the event flag before putting to queue
        sleep(random())
        q.put(i)  # only put to unblock getter after clearing hb flag
        print(f'worker: {i}')


def main():
    for i in range(5):
        result = q.get()
        sleep(random()/10)
        print(f'main[{i}]: {result}')
        hb.set()


threads = [Thread(target=t)
           for t in [main, worker]]
for t in threads:
    t.start()
for t in threads:
    t.join()
print('bye')
