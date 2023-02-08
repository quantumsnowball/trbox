import asyncio
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor

from trbox.common.logger import Log, set_log_level
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln

set_log_level('INFO')


class Party:
    async def handle(self):
        pass

    async def run(self):
        while True:
            Log.info(Memo('running').by(self))
            await asyncio.sleep(1)
            asyncio.create_task(self.handle())


class A(Party):
    async def handle(self):
        Log.critical(Memo('greeting').by(self))
        await asyncio.sleep(1)


class B(Party):
    async def handle(self):
        Log.critical(Memo('greeting').by(self))
        await asyncio.sleep(1)


def main():
    async def worker():
        a = A()
        b = B()
        async with asyncio.TaskGroup() as tg:
            tg.create_task(a.run())
            tg.create_task(b.run())

    asyncio.run(worker())


if __name__ == '__main__':
    main()
