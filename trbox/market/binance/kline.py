from typing import Any

from pandas import to_datetime
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln, ppf
from trbox.event.broker import AuditRequest
from trbox.event.market import Kline
from trbox.market.binance import BinanceWebsocket


class BinanceKlineStreaming(BinanceWebsocket):
    def __init__(self,
                 *args,
                 interval: str = '1m',
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._interval = interval

    def on_data(self, d: dict[str, Any]) -> None:
        try:
            k = d['k']
            e = Kline(
                timestamp=to_datetime(int(k['T'])*1e6),
                symbol=d['s'],
                open=float(k['o']),
                high=float(k['h']),
                low=float(k['l']),
                close=float(k['c']),
                volume=float(k['v']),
                value_traded=float(k['q']),
                bar_finished=bool(k['x']),
            )
            self.trader.strategy.put(e)
            # if backtesting, broker also receive MarketEvent to simulate quote
            if self.trader.backtesting:
                self.trader.broker.put(e)
            # TODO other parties should decide when to audit
            self.trader.broker.put(AuditRequest(e.timestamp))
        except KeyError as e:
            Log.warning(Memo(repr(e), 'check fields',
                             d=ppf(d)).sparse().by(self))
        except Exception as e:
            Log.exception(e)

    @override
    def start(self) -> None:
        self.ws.start()
        Log.debug(Memo('started', cln(self.ws)).by(
            self).tag('thread', 'socket'))
        self.ws.kline(self._symbol, 1, self._interval, self.on_data)
        Log.info(Memo(f'requested trade stream from {cln(self.ws)}')
                 .by(self).tag('stream', 'socket'))
