from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.common.utils import cln, ppf
from trbox.event import Event, MarketEvent
from trbox.event.broker import OrderResult
from trbox.event.handler import CounterParty
from trbox.event.market import Candlestick, Kline, OhlcvWindow
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
    def __init__(
        self, *,
        name: str | None = None,
        on_tick: Callable[['Strategy', Candlestick], None] | None = None,
        on_kline: Callable[['Strategy', Kline], None] | None = None,
        on_window: Callable[['Strategy', OhlcvWindow], None] | None = None
    ) -> None:
        super().__init__()
        self._name = name
        # event action hook
        self._on_tick = on_tick
        self._on_kline = on_kline
        self._on_window = on_window
        # bar counting
        self._count = Count()
        self._contexts = {}
        self._dos = {}

    def __str__(self) -> str:
        return f'{cln(self)}(name={self.name})'

    def on(self,
           symbol: Symbol,
           MarketEventClass: type[MarketEvent],
           *,
           do):
        index = (symbol, MarketEventClass)
        assert index not in self._contexts, 'Duplicated hook'
        self._contexts[index] = Context(strategy=self,
                                        count=Count())
        assert index not in self._dos, 'Duplicated hook'
        self._dos[index] = do
        return self

    @property
    def name(self) -> str | None:
        return self._name

    def handle_market_event(self, e: MarketEvent):
        index = (e.symbol, type(e))
        my = self._contexts[index]
        my.enent = e
        self._dos[index](my)
        my.count.tick()

    def handle(self, e: Event) -> None:
        if self.trader.backtesting:
            self.trader.signal.broker_ready.wait(5)
        # # for live streaming data
        # if self._on_tick:
        #     if isinstance(e, Candlestick):
        #         self._on_tick(self, e)
        #         self.count.tick()
        #         # TODO also Strategy need to know the number of Tick event
        #         # so maybe inc a counter state var here
        #         self.trader.signal.heartbeat.set()
        # if self._on_kline:
        #     if isinstance(e, Kline):
        #         self._on_kline(self, e)
        #         self.count.tick()
        #         self.trader.signal.heartbeat.set()
        # # for request and response data
        # if self._on_window:
        #     # upon receive window data, process using hook function
        #     if isinstance(e, OhlcvWindow):
        #         self._on_window(self, e)
        #         self.count.tick()
        #         # tell paper market to send next market event
        #         self.trader.signal.heartbeat.set()
        if isinstance(e, MarketEvent):
            if isinstance(e, Candlestick):
                self.handle_market_event(e)
                self.trader.signal.heartbeat.set()

        # on order result
        if isinstance(e, OrderResult):
            # TODO may be a on_fill callback?
            Log.info(Memo('order result', ppf(e))
                     .by(self).tag('order', 'confirmation').sparse())
