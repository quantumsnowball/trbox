from abc import ABC
from queue import Queue


class Party(ABC):
    def __init__(self) -> None:
        self.inbox = Queue()

    def connect(self, *,
                algo: 'Algo',
                market: 'Market',
                strategy: 'Strategy'):
        self.algo = algo
        self.market = market
        self.strategy = strategy


class Algo:
    def __init__(self,
                 market: 'Market',
                 strategy: 'Strategy') -> None:
        self.parties = (market, strategy,)
        for party in self.parties:
            party.connect(algo=self,
                          market=market,
                          strategy=strategy)


class Market(Party):
    def handle(self):
        self.strategy.inbox.put('hi')


class Strategy(Party):
    pass


def main() -> None:
    Algo(market=Market(),
         strategy=Strategy())


if __name__ == '__main__':
    main()
