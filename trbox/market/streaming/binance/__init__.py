from binance.websocket.spot.websocket_client import SpotWebsocketClient
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.common.utils import cln, ppf
from trbox.event.market import Candlestick
from trbox.market.streaming import StreamingSource


class BinanceWebsocket(StreamingSource):
    def __init__(self, *,
                 symbol: Symbol) -> None:
        super().__init__()
        self._symbol = symbol

    @override
    def start(self) -> None:
        def on_trade(d: dict[str, str]) -> None:
            try:
                price = float(d['p'])
                self.send.new_market_data(Candlestick(self._symbol, price))
                Log.debug(Memo('Trade',
                               symbol=d['s'], price=d['p'], quantity=d['q'])
                          .by(self).tag('trade', 'binance'))
            except KeyError as e:
                Log.warning(Memo(repr(e), 'check fields', d=ppf(d)).sparse()
                            .by(self))
            except Exception as e:
                Log.exception(e)

        ws = SpotWebsocketClient()
        ws.start()
        Log.debug(Memo('started', cln(ws)).by(self).tag('thread', 'socket'))
        ws.trade(self._symbol, 1, on_trade)
        Log.info(Memo(f'requested trade stream from {cln(ws)}')
                 .by(self).tag('stream', 'socket'))
        self._ws = ws

    @ override
    def stop(self) -> None:
        self._ws.stop()
