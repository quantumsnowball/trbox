from asyncio import Future
from typing import Any

from typing_extensions import override
from websockets.server import serve

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

    @override
    async def main(self):
        async with serve(self.echo, port=self.port):
            await Future()  # run forever

    async def echo(self, websocket):
        async for message in websocket:
            Log.critical(message)
            await websocket.send(message)
