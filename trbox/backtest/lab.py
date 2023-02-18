import glob
import os
from asyncio import Future, new_event_loop
from threading import Thread
from typing import Any, Generator

import click
from aiohttp import web
from binance.websocket.binance_socket_manager import json
from socketio.asyncio_client import asyncio
from typing_extensions import override

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9000
DEFAULT_PATH = '.'

routes = web.RouteTableDef()


def scan_for_st_recursive(path: str,
                          *,
                          prefix: str = 'st_') -> Generator[os.DirEntry[str], None, None]:
    for item in os.scandir(path):
        if item.is_dir():
            yield from scan_for_st_recursive(item.path)
        if item.is_file() and item.name.startswith(prefix):
            yield item


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
        paths = [dict(name=m.name, path=m.path)
                 for m in scan_for_st_recursive(self._path)]
        return web.json_response(paths,
                                 dumps=lambda s: json.dumps(s, indent=4))

    # TODO: propose definition of a `lab` dir:
    # 1. contains a single st_*.py file
    # 2. can have subdir or any other files
    # TODO: to create a lab in frontend:
    # 1. scan cwd for a st_*.py
    # 2. copy to new subdir and copy the original st_*.py into it

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
