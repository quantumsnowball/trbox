from logging import debug
from typing import Self
from trbox.common.utils import cln
from trbox.event import Event
from trbox.event.handler import CounterParty
from trbox.event.market import MarketDataRequest
from trbox.event.system import Exit, Start
from trbox.trader import Trader
from trbox.market.datasource import DataSource
from trbox.market.datasource.streaming import StreamingSource
from trbox.market.datasource.onrequest import OnRequestSource


class Market(CounterParty):
    def __init__(self, *,
                 source: DataSource) -> None:
        super().__init__()
        self._source = source

    def attach(self, trader: Trader
               ) -> Self:
        # this will also attach DataSource in Market is init-ed
        self._source.attach(trader)
        return super().attach(trader)

    def handle(self, e: Event) -> None:
        # listen to system Start event
        if isinstance(e, Start):
            if isinstance(self._source, StreamingSource):
                self._source.start()
                debug((f'{cln(self)} '
                       f'started {cln(self._source)}.'))
        # listen to MarketDataRequest from Strategy
        if isinstance(e, MarketDataRequest):
            if isinstance(self._source, OnRequestSource):
                self._source.on_request(e)
                debug((f'{cln(self)} '
                       f'issued {cln(self._source)}.'))
        # listen to Exit event to also close any threaded DataSource
        if isinstance(e, Exit):
            if isinstance(self._source, StreamingSource):
                self._source.stop()
                debug((f'{cln(self)} '
                       f'requested {cln(self._source)} to stop and close.'))
