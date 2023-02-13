from asyncio import Future
from typing import Any, Set

import websockets
from typing_extensions import override
from websockets.legacy.protocol import broadcast
from websockets.server import WebSocketServerProtocol, serve

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console.services import Service
from trbox.console.services.message import Message


#
# websocket
#
class WebSocketService(Service):
    def __init__(self,
                 *args: Any,
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._ws: WebSocketServerProtocol | None = None
        self._clients: Set[WebSocketServerProtocol] = set()

    @property
    def clients(self) -> Set[WebSocketServerProtocol]:
        return self._clients

    # ws_handle
    async def register(self, client: WebSocketServerProtocol):
        self._clients.add(client)
        Log.warning(Memo('Connected', n_conn=len(self.clients), e=client)
                    .by(self).tag('client', 'connected'))
        try:
            await client.wait_closed()
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
    def send(self, message: Message) -> None:
        # broadcast Message to all currently connected clients
        async def task() -> None:
            broadcast(self.clients, message.json)
        self.create_task(task())
