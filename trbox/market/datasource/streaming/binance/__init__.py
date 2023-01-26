from logging import debug, exception, info, warning
from typing_extensions import override
from binance.websocket.spot.websocket_client import SpotWebsocketClient
from trbox.common.types import Symbol
from trbox.common.utils import cln
from trbox.event.market import Candlestick
from trbox.market.datasource.streaming import StreamingSource


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
                debug(f'price<{type(price)}>: {price}')
            except KeyError:
                warning(f'{cln(self)}: `p` field not available yet')
            except Exception as e:
                exception(e)

        ws = SpotWebsocketClient()
        ws.start()
        debug(f'{cln(self)}: {cln(ws)} started')
        ws.trade(self._symbol, 1, on_trade)
        info(f'{cln(self)}: {cln(ws)} request trade stream')
        self._ws = ws

    @override
    def stop(self) -> None:
        self._ws.stop()
