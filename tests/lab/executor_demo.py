import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from time import sleep

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo


class Strategy:
    def __init__(self) -> None:
        self.queue = Queue()
        self.pool = ThreadPoolExecutor()

    def put(self, e) -> None:
        self.queue.put(e)

    async def handle(self, e) -> None:
        await asyncio.sleep(5)
        Log.critical(f'Processed {e} after 5 seconds')

    def run(self) -> None:
        async def worker():
            while True:
                loop = asyncio.get_event_loop()
                # if I use the party_pool, it is still blocking, failed
                e = await loop.run_in_executor(self.pool, self.queue.get)
                # Log.critical(Memo(e=e).by(self))
                loop.create_task(self.handle(e))
        asyncio.run(worker())


class Market:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def run(self) -> None:
        for i in range(50):
            sleep(1)
            self.strategy.put(f'Event({i})')
            # Log.critical('Market: sent Event')


class Algo:
    def __init__(self) -> None:
        self.st = Strategy()
        self.mk = Market(self.st)

    def run(self) -> None:
        with ThreadPoolExecutor() as party_pool:
            party_pool.submit(self.st.run)
            party_pool.submit(self.mk.run)


def main() -> None:
    Algo().run()


if __name__ == '__main__':
    main()
