import asyncio
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Any

from trbox.common.logger import Log, set_log_level
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln

set_log_level('INFO')


class Event:
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f'{cln(self)}({self.name})'


class Party:
    def __init__(self):
        self.inbox = Queue()

    @abstractmethod
    async def handle(self, e):
        pass

    async def greeting(self):
        await asyncio.sleep(1)
        Log.critical('greeting')

    def run(self):
        async def checkmail():
            while True:
                e = await self.inbox.get()
                Log.critical(Memo('got event', e=e))
                asyncio.create_task(self.greeting())
                Log.critical('created task')
        asyncio.run(checkmail())


class Market(Party):
    def attach(self, st: 'Strategy'):
        self.st = st

    async def handle(self, e: Any):
        Log.info(Memo('I will keep sending market data to st', e=e).by(self))
        for i in range(20):
            self.st.inbox.put(Event(f'market data ({i})'))
            await asyncio.sleep(1)


class Strategy(Party):
    def attach(self, mk: Market):
        self.mk = mk

    async def handle_long_task(self):
        await asyncio.sleep(5)
        Log.critical(Memo('finally finished processing').by(self))

    async def handle(self, e: Any):
        Log.info(Memo('got and event', e=e).by(self))
        asyncio.create_task(self.handle_long_task())


class Algo:
    def __init__(self):
        self.mk = Market()
        self.st = Strategy()
        self.mk.attach(self.st)
        self.st.attach(self.mk)

        self.handlers = [self.mk, self.st]

    def run(self):
        with ThreadPoolExecutor() as exe:
            self.mk.inbox.put(Event('start'))
            for h in self.handlers:
                exe.submit(h.run)
            Log.warning('blocked here, like thread.join()')


def main():
    algo = Algo()
    algo.run()


if __name__ == '__main__':
    main()
