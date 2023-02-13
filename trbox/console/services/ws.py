from __future__ import annotations

from asyncio import Future
from typing import TYPE_CHECKING, Any, Set

from typing_extensions import override
from websockets.exceptions import ConnectionClosedError
from websockets.legacy.protocol import broadcast
from websockets.server import WebSocketServerProtocol, serve

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console.services import Service
from trbox.console.services.message import Message
from trbox.event.portfolio import (EquityCurveHistoryRequest,
                                   OrderResultHistoryRequest)

if TYPE_CHECKING:
    from trbox.console.dashboard import TrboxDashboard

DEFAULT_HISTORY_LENGTH: int | None = None

#
# websocket
#


class WebSocketService(Service):
    def __init__(self,
                 *args: Any,
                 host: TrboxDashboard,
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._host = host
        self._ws: WebSocketServerProtocol | None = None
        self._clients: Set[WebSocketServerProtocol] = set()

    @property
    def clients(self) -> Set[WebSocketServerProtocol]:
        return self._clients

    # ws_handle
    async def register(self, client: WebSocketServerProtocol):
        # a client just connected here
        self._clients.add(client)
        Log.warning(Memo('Connected', n_conn=len(self.clients), e=client)
                    .by(self).tag('client', 'connected'))
        # from here client will start to receive live updating messages
        try:
            # keep listening for incoming message request
            async for msg in client:
                if msg == 'EquityValueHistoryRequest':
                    self._host.portfolio.put(
                        EquityCurveHistoryRequest(client=client,
                                                  n=DEFAULT_HISTORY_LENGTH))
                elif msg == 'TradeLogHistoryRequest':
                    self._host.portfolio.put(
                        OrderResultHistoryRequest(client=client,
                                                  n=DEFAULT_HISTORY_LENGTH))
            # await client.wait_closed()
        except ConnectionClosedError as e:
            Log.warning(Memo('Client has closed the connection', e=e)
                        .by(self).tag('client', 'disconnected'))
            # self._clients.remove(client)
        finally:
            self._clients.remove(client)
            Log.warning(Memo('Disconnected', n_conn=len(self.clients), e=client)
                        .by(self).tag('client', 'disconnected'))

    @override
    async def main(self) -> None:
        # this function create a connection for each client
        async with serve(self.register, port=self.port):
            #
            await Future()  # run forever

    #
    # helpers
    #
    def broadcast(self, message: Message) -> None:
        # broadcast Message to all currently connected clients
        async def task() -> None:
            broadcast(self.clients, message.json)
        self.create_task(task())

    def send(self, client: WebSocketServerProtocol, message: Message) -> None:
        # only send to a single client
        async def task() -> None:
            await client.send(message.json)
        self.create_task(task())
