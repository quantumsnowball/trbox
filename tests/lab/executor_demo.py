import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from time import sleep

from trbox.common.logger import Log, set_log_level
from trbox.common.logger.parser import Memo

set_log_level('INFO')


class Party:
    def attach(self, *,
               algo: 'Algo',
               strategy: 'Strategy',
               market: 'Market') -> None:
        self.algo = algo
        self.strategy = strategy
        self.market = market


class Strategy(Party):
    def __init__(self) -> None:
        self.inbox = Queue()

    async def trade(self, e) -> None:
        await asyncio.sleep(5)
        Log.critical(f'decided to trade on {e} after 5 seconds')

    async def handle(self, e) -> None:
        await asyncio.sleep(5)
        Log.critical(f'Processed {e} after 5 seconds')
        await self.trade(e)

        pass

    def run(self) -> None:
        async def worker():
            while True:
                try:
                    e = await asyncio.to_thread(self.inbox.get)
                    Log.critical(Memo(e=e).by(self))
                    asyncio.create_task(self.handle(e))
                except Exception as e:
                    Log.exception(e)
        asyncio.run(worker())


class Market(Party):
    def run(self) -> None:
        for i in range(10):
            sleep(1)
            self.strategy.inbox.put(f'Event({i})')
            # Log.critical('Market: sent Event')


class Algo:
    def __init__(self, *,
                 market: Market,
                 strategy: Strategy) -> None:
        self.parties = (market, strategy)
        for p in self.parties:
            p.attach(algo=self,
                     strategy=strategy,
                     market=market)

    def run(self) -> None:
        with ThreadPoolExecutor() as party_pool:
            for party in self.parties:
                party_pool.submit(party.run)


def main() -> None:
    Algo(market=Market(),
         strategy=Strategy()).run()


if __name__ == '__main__':
    main()
