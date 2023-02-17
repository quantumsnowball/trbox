from asyncio import Future
from threading import Thread

from aiohttp import web
from socketio.asyncio_client import asyncio
from typing_extensions import override

routes = web.RouteTableDef()


@routes.get('/')
async def hello(request):
    return web.Response(text="Hello, world")


class Lab(Thread):
    def __init__(self,
                 port: int = 9000) -> None:
        super().__init__()
        self._port = port
        self._app = web.Application()
        self._app.add_routes(routes)
        self._runner = web.AppRunner(self._app)

    async def serve(self):
        await self._runner.setup()
        site = web.TCPSite(self._runner, port=self._port)
        await site.start()
        await Future()  # run forever

    @override
    def run(self) -> None:
        asyncio.run(self.serve())
