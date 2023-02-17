import os
from asyncio import Future
from threading import Thread
from typing import Any

import click
from aiohttp import web
from socketio.asyncio_client import asyncio
from typing_extensions import override

routes = web.RouteTableDef()


@routes.get('/')
async def lsdir(_):
    txt = ''
    for dirpath, dirname, filename in os.walk('.'):
        txt += f'{dirpath}\t{dirname}\t{filename}\n'

    return web.Response(text=txt)


class Lab(Thread):
    def __init__(self,
                 *args: Any,
                 port: int = 9000,
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._port = port
        self._app = web.Application()
        self._app.add_routes(routes)
        self._runner = web.AppRunner(self._app)

    async def serve(self) -> None:
        click.echo(f'Serving at http://localhost:{self._port}')
        await self._runner.setup()
        site = web.TCPSite(self._runner, port=self._port)
        await site.start()
        await Future()  # run forever

    @override
    def run(self) -> None:
        asyncio.run(self.serve())
