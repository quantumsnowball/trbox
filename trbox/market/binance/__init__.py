from abc import ABC

from binance.websocket.spot.websocket_client import SpotWebsocketClient
from typing_extensions import override

from trbox.common.types import Symbol
from trbox.market import Market


class BinanceWebsocket(Market, ABC):
    def __init__(self, *,
                 symbol: Symbol) -> None:
        super().__init__()
        self._symbol = symbol
        self._ws = SpotWebsocketClient()

    @property
    def ws(self) -> SpotWebsocketClient:
        return self._ws

    @ override
    def stop(self) -> None:
        self._ws.stop()
