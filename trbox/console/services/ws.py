from asyncio import Future
from typing import Any

from typing_extensions import override
from websockets.server import WebSocketServerProtocol, serve

from trbox.common.logger import Log
from trbox.console.services import Service


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
    async def main(self):
        async with serve(self.ws_handle, port=self.port):
            await Future()  # run forever

    async def ws_handle(self, websocket: WebSocketServerProtocol):
        self._ws = websocket
        async for message in websocket:
            Log.critical(message)
            await websocket.send(message)

    #
    # helpers
    #
    def send(self, msg: str):
        # TODO when a 2nd client connected, the 1st client stop receiving updates
        async def task():
            assert self._ws is not None
            await self._ws.send(msg)
        self.create_task(task())
