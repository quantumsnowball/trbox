from collections import defaultdict
from dataclasses import dataclass

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.common.utils import cln, ppf
from trbox.event import Event, MarketEvent
from trbox.event.broker import OrderResult
from trbox.event.handler import CounterParty
from trbox.trader import Trader


class Count:
    def __init__(self) -> None:
        self._i: dict[int, int] = defaultdict(lambda: 0)
        self._initial = True

    @property
    def beginning(self) -> bool:
        return self._initial

    def tick(self) -> None:
        if self._initial:
            self._initial = False
        for n, i in self._i.items():
            if i >= n:
                self._i[n] = 1
            else:
                self._i[n] += 1

    def every(self,
              n: int, *,
              initial: bool = False) -> bool:
        if self._i[n] >= n:
            return True
        if initial:
            return self._initial
        return False


@dataclass
class Context:
    strategy: 'Strategy'
    count: Count
    event: MarketEvent | None = None

    @property
    def trader(self) -> Trader:
        return self.strategy.trader


class Strategy(CounterParty):
    def __init__(self, *,
                 name: str | None = None,) -> None:
        super().__init__()
        self._name = name
        # bar counting
        self._contexts = {}
        self._dos = {}

    def __str__(self) -> str:
        return f'{cln(self)}(name={self.name})'

    @property
    def name(self) -> str | None:
        return self._name

    def on(self,
           symbol: Symbol,
           MarketEventClass: type[MarketEvent],
           *,
           do):
        # uniquely identify a data handler
        index = (symbol, MarketEventClass)
        assert index not in self._contexts, 'Duplicated hook'
        # prepare bundle for handle to do its things
        self._contexts[index] = Context(strategy=self,
                                        count=Count())
        assert index not in self._dos, 'Duplicated hook'
        # prepare the data handler
        self._dos[index] = do
        return self

    def handle_market_event(self, e: MarketEvent):
        # select the data handler
        index = (e.symbol, type(e))
        context = self._contexts[index]
        handler = self._dos[index]
        # set the event object in runtime
        context.event = e
        # call the data handler
        handler(my=context)
        # tick the counter
        context.count.tick()

    def handle(self, e: Event) -> None:
        if self.trader.backtesting:
            self.trader.signal.broker_ready.wait(5)

        if isinstance(e, MarketEvent):
            self.handle_market_event(e)
            self.trader.signal.heartbeat.set()

        # on order result
        if isinstance(e, OrderResult):
            # TODO may be a on_fill callback?
            Log.info(Memo('order result', ppf(e))
                     .by(self).tag('order', 'confirmation').sparse())
