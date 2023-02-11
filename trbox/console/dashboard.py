from socketio.asyncio_client import asyncio
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console import Console
from trbox.console.services.nextjs_site import NextSite
from trbox.console.services.ws import WebSocketService
from trbox.event import Event
from trbox.event.portfolio import EquityCurveUpdate


class TrboxDashboard(Console):
    def __init__(self,
                 website_port: int = 5000,
                 websocket_port: int = 8000) -> None:
        super().__init__()
        self._website = NextSite(port=website_port,
                                 daemon=True)
        self._websocket = WebSocketService(port=websocket_port,
                                           daemon=True)

    @property
    def website(self) -> NextSite:
        return self._website

    @property
    def websocket(self) -> WebSocketService:
        return self._websocket

    @override
    def start(self) -> None:
        self._website.start()
        self._websocket.start()

        Log.info(Memo(f'Starting website on port {self._website.port}'
                      f' and websocket on port {self._websocket.port}')
                 .by(self))

    @override
    def stop(self) -> None:
        Log.error('Need to stop the event loop')

    #
    # handle party events
    #

    def handle_equity_curve_update(self, e: EquityCurveUpdate):
        self._websocket.send(f'equity={e.equity}')

    @override
    def handle(self, e: Event) -> None:
        super().handle(e)
        # be careful must not block after this point
        if isinstance(e, EquityCurveUpdate):
            self.handle_equity_curve_update(e)
