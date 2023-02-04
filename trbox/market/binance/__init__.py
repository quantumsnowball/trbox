from abc import ABC, abstractmethod

from binance.websocket.spot.websocket_client import SpotWebsocketClient
from pandas import to_datetime
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.common.utils import cln, ppf
from trbox.event.market import Candlestick
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
