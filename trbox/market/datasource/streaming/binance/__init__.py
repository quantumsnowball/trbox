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

    def on_server_time(self) -> None:
        pass

    @override
    def start(self) -> None:
        def on_trade(d: dict) -> None:
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
        try:
            ws.trade(self._symbol, 1, on_trade)
            info(f'{cln(self)}: {cln(ws)} request trade stream')
            ws.join()
            info(f'{cln(self)}: joined {cln(ws)} thread')
        except KeyboardInterrupt as kb:
            warning(f'{cln(self)}: {cln(kb)}')
        except Exception as e:
            raise e
        finally:
            ws.stop()
            debug(f'{cln(self)}: {cln(ws)} stopped')
            ws.close()
            debug(f'{cln(self)}: {cln(ws)} closed')
