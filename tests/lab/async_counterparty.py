import asyncio
from concurrent.futures import ThreadPoolExecutor

from trbox.common.logger import Log, set_log_level
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln

set_log_level('INFO')


class Party:
    async def run(self):
        while True:
            Log.info(Memo('running').by(self))
            await asyncio.sleep(1)


class A(Party):
    pass


class B(Party):
    pass


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
