from typing import Any

from pandas import to_datetime
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln, ppf
from trbox.event.broker import AuditRequest
from trbox.event.market import TradeTick
from trbox.market.binance import BinanceWebsocket


class BinanceStreamingTrades(BinanceWebsocket):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def on_data(self, d: dict[str, str]) -> None:
        try:
            price = float(d['p'])
            datetime = to_datetime(int(d['E'])*1e6)
            e = TradeTick(datetime, self._symbol, price)

            self.strategy.put(e)
            # if backtesting, broker also receive MarketEvent to simulate quote
            if self.trader.backtesting:
                self.broker.put(e)
            # TODO other parties should decide when to audit
            self.broker.put(AuditRequest(e.timestamp))

            Log.debug(Memo('Trade',
                           symbol=d['s'], price=d['p'], quantity=d['q'])
                      .by(self).tag('trade', 'binance'))
        except KeyError as e:
            Log.warning(Memo(repr(e), 'check fields', d=ppf(d)).sparse()
                        .by(self))
        except Exception as e:
            Log.exception(e)

    @override
    def start(self) -> None:
        self.ws.start()
        Log.debug(Memo('started', cln(self.ws)).by(
            self).tag('thread', 'socket'))
        self.ws.trade(self._symbol, 1, self.on_data)
        Log.info(Memo(f'requested trade stream from {cln(self.ws)}')
                 .by(self).tag('stream', 'socket'))
