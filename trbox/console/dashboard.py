from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console import Console
from trbox.console.services.message import (EquityCurve, EquityCurveHistory,
                                            OrderResult, TradeLogHistory)
from trbox.console.services.nextjs_site import NextSite
from trbox.console.services.ws import WebSocketService
from trbox.event import Event
from trbox.event.portfolio import (EquityCurveHistoryRequest,
                                   EquityCurveHistoryUpdate, EquityCurveUpdate,
                                   OrderResultHistoryRequest,
                                   OrderResultHistoryUpdate, OrderResultUpdate)


class TrboxDashboard(Console):
    def __init__(self,
                 website_port: int = 5000,
                 websocket_port: int = 8000) -> None:
        super().__init__()
        self._website = NextSite(port=website_port,
                                 daemon=True)
        self._websocket = WebSocketService(port=websocket_port,
                                           daemon=True,
                                           host=self)

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

    def handle_equity_curve_update(self, e: EquityCurveUpdate) -> None:
        self.websocket.broadcast(EquityCurve(e))

    def handle_order_result_update(self, e: OrderResultUpdate) -> None:
        self.websocket.broadcast(OrderResult(e))

    def handle_equity_curve_history_update(self, e: EquityCurveHistoryUpdate) -> None:
        self.websocket.send(e.client, EquityCurveHistory(e))

    def handle_order_result_history_update(self, e: OrderResultHistoryUpdate) -> None:
        self.websocket.send(e.client, TradeLogHistory(e))

    @override
    def handle(self, e: Event) -> None:
        super().handle(e)
        # be careful must not block after this point
        if isinstance(e, EquityCurveUpdate):
            self.handle_equity_curve_update(e)
        elif isinstance(e, OrderResultUpdate):
            self.handle_order_result_update(e)
        elif isinstance(e, EquityCurveHistoryUpdate):
            self.handle_equity_curve_history_update(e)
        elif isinstance(e, OrderResultHistoryUpdate):
            self.handle_order_result_history_update(e)
