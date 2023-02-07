import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from time import sleep

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo


class Market:
    def __init__(self, strategy):
        self.strategy = strategy

    def run(self):
        for i in range(50):
            sleep(1)
            self.strategy.put(f'Event({i})')
            Log.critical('Market: sent Event')


class Strategy:
    def __init__(self) -> None:
        self.queue = Queue()

    def put(self, e):
        self.queue.put(e)

    async def handle(self, e):
        await asyncio.sleep(5)
        Log.critical(f'Processed {e} after 5 seconds')

    def run(self):
        async def worker():
            while True:
                loop = asyncio.get_event_loop()
                e = await loop.run_in_executor(None, self.queue.get)
                Log.critical(Memo(e=e).by(self))
                loop.create_task(self.handle(e))
        asyncio.run(worker())


class Algo:
    def __init__(self) -> None:
        self.st = Strategy()
        self.mk = Market(self.st)

    def run(self):
        with ThreadPoolExecutor() as exe:
            for h in [self.st, self.mk]:
                exe.submit(h.run)


def main():
    Algo().run()


if __name__ == '__main__':
    main()
