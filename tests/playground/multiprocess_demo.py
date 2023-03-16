from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Process
from queue import Queue
from time import sleep


class Handler:
    def __init__(self):
        self.queue = Queue()  # this object is essential, but not picklable

    def put(self, item):
        self.queue.put(item)

    def run(self):
        while True:
            sleep(1)
            item = self.queue.get()
            if item == 'exit':
                break
            # do other things on the item ...
            print(item)


class Runner:
    def __init__(self, name):
        self.name = name
        self.a = Handler()
        self.b = Handler()

    def start(self):
        for i in range(4):
            self.a.put(f'{self.name}: hello a ({i})')
            self.b.put(f'{self.name}: hello b ({i})')
        self.a.put('exit')
        self.b.put('exit')
        with ThreadPoolExecutor() as exe:
            futures = [exe.submit(r.run) for r in [self.a, self.b]]
        for future in futures:
            future.result()


# current implementation
def run_in_multi_thread():
    rA = Runner('A')
    rB = Runner('B')
    rC = Runner('C')
    with ThreadPoolExecutor() as exe:
        futures = [exe.submit(r.start) for r in [rA, rB, rC]]
        for future in futures:
            future.result()


# how to implement this?
def run_in_multi_process_pool():
    rA = Runner('A')
    rB = Runner('B')
    rC = Runner('C')
    with ProcessPoolExecutor() as exe:
        futures = [exe.submit(r.start) for r in [rA, rB, rC]]
        for future in futures:
            future.result()


def run_in_process():
    rA = Runner('A')
    rB = Runner('B')
    rC = Runner('C')
    procs = [Process(target=r.start) for r in [rA, rB, rC]]
    for p in procs:
        p.start()
    for p in procs:
        p.join()


if __name__ == '__main__':
    # run_in_multi_thread()  # this is currently running fine
    # run_in_multi_process_pool()  # this doesn't work, need to make everything picklable
    run_in_process()
