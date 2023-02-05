import threading
from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.common.utils import cln, ppf
from trbox.event import Event, MarketEvent
from trbox.event.broker import OrderResult
from trbox.event.handler import CounterParty
from trbox.event.system import Start
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


# Hook = Callable[[Context], None]
class Hook(Protocol):
    def __call__(self, my: Context) -> None:
        ...


@dataclass
class DataHandler:
    context: Context
    hook: Hook


DataStreamId = tuple[Symbol, type[MarketEvent]]

DataHandlers = dict[DataStreamId, DataHandler]

Heartbeats = dict[DataStreamId, threading.Event]


class Strategy(CounterParty):
    def __init__(self, *,
                 name: str | None = None,) -> None:
        super().__init__()
        self._name = name
        self._datahandlers: DataHandlers = {}
        # signal
        self._heartbeats: Heartbeats = {}

    def __str__(self) -> str:
        return f'{cln(self)}(name={self.name})'

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def heartbeats(self) -> Heartbeats:
        return self._heartbeats

    def on(self,
           symbol: Symbol,
           MarketEventClass: type[MarketEvent],
           *,
           do: Hook) -> 'Strategy':
        # uniquely identify a data handler
        index = (symbol, MarketEventClass)
        assert index not in self._datahandlers, 'Duplicated hook'
        # prepare bundle for datahandler to do its things
        self._datahandlers[index] = DataHandler(
            context=Context(strategy=self,
                            count=Count()),
            hook=do)
        # create heartbeat events for every DataStreamId
        self.heartbeats[index] = threading.Event()
        return self

    def handle_market_event(self, e: MarketEvent):
        # select the data handler
        index = (e.symbol, type(e))
        handler = self._datahandlers[index]
        context = handler.context
        hook = handler.hook
        # set the event object in runtime
        context.event = e
        # call the data handler hook function
        hook(my=context)
        # tick the counter
        context.count.tick()
        # set heartbeat event
        self._heartbeats[index].set()

    def handle(self, e: Event) -> None:
        if isinstance(e, Start):
            for _, hb in self.heartbeats.items():
                hb.set()

        Log.critical('yeah waiting for broker_ready')
        if self.trader.backtesting:
            self.trader.signal.broker_ready.wait(5)

        if isinstance(e, MarketEvent):
            self.handle_market_event(e)

        # on order result
        if isinstance(e, OrderResult):
            # TODO may be a on_fill callback?
            Log.info(Memo('order result', ppf(e))
                     .by(self).tag('order', 'confirmation').sparse())
