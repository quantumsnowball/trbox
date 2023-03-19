from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Process
from queue import Queue
from time import sleep

# from multiprocessing import Queue


class Handler:
    def __init__(self):
        self.queue = Queue()  # this object is essential

    def put(self, item):
        self.queue.put(item)

    def run(self):
        while True:
            item = self.queue.get()
            if item == 'exit':
                break
            # do other things on the item ...
            print(item)
            sleep(1)


class Runner:
    def __init__(self, name):
        self.name = name
        self.a = Handler()
        self.b = Handler()

    def start(self):
        # some dummy messages
        for _ in range(3):
            self.a.put(f'{self.name}: hello a')
            self.b.put(f'{self.name}: hello b')
        self.a.put('exit')
        self.b.put('exit')
        with ThreadPoolExecutor() as exe:
            futures = [exe.submit(r.run) for r in [self.a, self.b]]
            for f in futures:
                f.result()


# this requires everything to be picklable
def run_in_process_pool():
    rA = Runner('A')
    rB = Runner('B')
    rC = Runner('C')
    with ProcessPoolExecutor() as exe:
        futures = [exe.submit(r.start) for r in [rA, rB, rC]]
        for future in futures:
            future.result()


# this does not pickle anythin, but why?
def run_in_processes():
    rA = Runner('A')
    rB = Runner('B')
    rC = Runner('C')
    procs = [Process(target=r.start) for r in [rA, rB, rC]]
    for p in procs:
        p.start()
    for p in procs:
        p.join()


if __name__ == '__main__':
    # run_in_process_pool()  # `TypeError: cannot pickle '_thread.lock' object`
    run_in_processes()  # this is working
