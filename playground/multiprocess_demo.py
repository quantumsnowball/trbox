from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Process, Queue
# from queue import Queue
from time import sleep


class Handler(ABC):
    def __init__(self):
        self.queue = Queue()  # this object is essential, but not picklable

    def put(self, item):
        self.queue.put(item)

    @abstractmethod
    def run(self):
        pass


class Monitor(Handler):
    def __init__(self):
        super().__init__()
        self.count = 0

    def run(self):
        while True:
            item = self.queue.get()
            if item == 'exit':
                break
            self.count += 1
            # print(f'msg count = {self.count}')


monitor = Monitor()


class Worker(Handler):
    def __init__(self):
        super().__init__()
        self.last_msg = 'init'

    def run(self):
        while True:
            item = self.queue.get()
            self.last_msg = item
            if item == 'exit':
                break
            # do other things on the item, may be cpu intensive ...
            # print(item)
            monitor.put('count me')


class Runner:
    def __init__(self, name):
        self.name = name
        self.a = Worker()
        self.b = Worker()

    def start(self):
        for i in range(4):
            self.a.put(f'{self.name}: hello a ({i})')
            self.b.put(f'{self.name}: hello b ({i})')
        self.a.put('exit')
        self.b.put('exit')
        monitor.put('exit')
        with ThreadPoolExecutor() as exe:
            futures = [exe.submit(r.run)
                       for r in [self.a, self.b]]
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
    print(rA.a.last_msg)
    procs = [*[Process(target=r.start)
             for r in [rA, rB, rC]], Process(target=monitor.run)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print(rA.a.last_msg)


if __name__ == '__main__':
    # run_in_multi_thread()  # this is currently running fine
    # run_in_multi_process_pool()  # this doesn't work, need to make everything picklable
    run_in_process()
