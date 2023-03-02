import threading
from typing import TypeVar

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.common.utils import cln, ppf
from trbox.event import Event, MarketEvent
from trbox.event.broker import OrderResult
from trbox.event.handler import CounterParty
from trbox.strategy.context import Context, Count
from trbox.strategy.types import DataHandler, DataHandlers, Heartbeats, Hook

T = TypeVar('T', bound=MarketEvent)


class Strategy(CounterParty):
    def __init__(self, *,
                 name: str) -> None:
        super().__init__()
        self._name = name
        self._datahandlers: DataHandlers = {}
        # signal
        self._heartbeats: Heartbeats = {}

    def __str__(self) -> str:
        return f'{cln(self)}(name={self.name})'

    @property
    def name(self) -> str:
        return self._name

    @property
    def heartbeats(self) -> Heartbeats:
        return self._heartbeats

    def on(self,
           symbol: Symbol,
           MarketEventClass: type[T],
           *,
           do: Hook[T]) -> 'Strategy':
        # uniquely identify a data handler
        index = (symbol, MarketEventClass)
        assert index not in self._datahandlers, 'Duplicated hook'
        # prepare bundle for datahandler to do its things
        self._datahandlers[index] = DataHandler(
            context=Context(strategy=self,
                            count=Count()),
            hook=do)
        # create heartbeat events for every DataStreamId
        heartbeat = threading.Event()
        heartbeat.set()
        self.heartbeats[index] = heartbeat
        return self

    def handle_market_event(self, e: MarketEvent) -> None:
        # select the data handler
        index = (e.symbol, type(e))
        handler = self._datahandlers.get(index, None)
        if not handler:
            return
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
        if self.trader.backtesting:
            self.trader.signal.broker_ready.wait(5)

        if isinstance(e, MarketEvent):
            self.handle_market_event(e)

        # on order result
        if isinstance(e, OrderResult):
            # TODO may be a on_fill callback?
            Log.info(Memo('order result', ppf(e))
                     .by(self).tag('order', 'confirmation').sparse())
