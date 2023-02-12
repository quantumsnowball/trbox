from asyncio import Future
from typing import Any

from typing_extensions import override
from websockets.server import WebSocketServerProtocol, serve

from trbox.common.logger import Log
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

    @override
    async def main(self) -> None:
        async with serve(self.ws_handle, port=self.port):
            await Future()  # run forever

    async def ws_handle(self, websocket: WebSocketServerProtocol) -> None:
        self._ws = websocket
        async for message in websocket:
            Log.critical(message)
            await websocket.send(message)

    #
    # helpers
    #
    def send(self, message: Message) -> None:
        # TODO when a 2nd client connected, the 1st client stop receiving updates
        async def task() -> None:
            assert self._ws is not None
            await self._ws.send(message.json)
        self.create_task(task())
