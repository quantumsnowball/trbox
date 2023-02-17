import glob
import os
from asyncio import Future, new_event_loop
from threading import Thread
from typing import Any

import click
from aiohttp import web
from socketio.asyncio_client import asyncio
from typing_extensions import override

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9000
DEFAULT_PATH = '.'

routes = web.RouteTableDef()


class Lab(Thread):
    def __init__(self,
                 path: str,
                 *args: Any,
                 host: str,
                 port: int,
                 **kwargs: Any) -> None:
        super().__init__(*args,
                         name='Lab',
                         **kwargs)
        self._path = path
        self._host = host
        self._port = port
        self._app = web.Application()
        self._app.add_routes([
            web.route('GET', '/', self.lsdir),
        ])
        self._runner = web.AppRunner(self._app)

    #
    # routes
    #
    async def lsdir(self, _) -> web.Response:
        txt = ''
        # for dirpath, dirname, filename in os.walk(self._path):
        #     txt += f'{dirpath}\t{dirname}\t{filename}\n'
        for f in glob.glob(f'{self._path}/**/*.py', recursive=True):
            basename = os.path.basename(f)
            dirname = os.path.dirname(f)
            txt += f'{dirname}\t{basename}\n'
        return web.Response(text=txt)

    #
    # main loop
    #
    async def serve(self) -> None:
        click.echo(f'Serving {self._path} at http://{self._host}:{self._port}')
        await self._runner.setup()
        site = web.TCPSite(self._runner, host=self._host, port=self._port)
        await site.start()
        await Future()  # run forever

    @override
    def run(self) -> None:
        asyncio.run(self.serve())
