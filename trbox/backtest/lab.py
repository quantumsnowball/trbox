import os
from asyncio import Future
from threading import Thread
from typing import Any, Union

import click
from aiohttp import web
from aiohttp.typedefs import Handler
from binance.websocket.binance_socket_manager import json
from socketio.asyncio_client import asyncio
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 7000
DEFAULT_PATH = '.'
FRONTEND_LOCAL_DIR = f'{os.path.dirname(__file__)}/../frontend/trbox-lab/out/'
DEFAULT_FILENAME = 'index.html'
ENTRY_POINT = f'{FRONTEND_LOCAL_DIR}{DEFAULT_FILENAME}'
SRC_PREFIX = 'st_'
RUNDIR_PREFIX = '.run'


TreeDict = dict[str, Union['TreeDict', None]]


def scan_for_st_recursive(path: str,
                          *,
                          prefix: str = SRC_PREFIX,
                          prefix_excluded: str = RUNDIR_PREFIX) -> TreeDict:
    d = dict()
    # loop through every items in path
    for m in os.scandir(path):
        if m.is_dir() and not m.name.startswith(prefix_excluded):
            # nested one level if is a dir, key is the dirname
            d[m.name] = scan_for_st_recursive(m.path)
        elif m.is_file() and m.name.startswith(prefix):
            # if a target file is found, set the key with None as value
            d[m.name] = None
    return d


def scan_for_run_recursive(path: str,
                           *,
                           prefix: str = RUNDIR_PREFIX) -> TreeDict:
    d = dict()
    # loop through every items in path
    for m in os.scandir(path):
        if m.is_dir():
            if m.name.startswith(prefix):
                # prefixed dir should contain run info
                d[m.name] = None
            else:
                # nested one level if is a dir, key is the dirname
                d[m.name] = scan_for_run_recursive(m.path)
    return d


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
        self._app = web.Application(middlewares=[self.on_request_error, ])
        self._app.add_routes([
            # match api first
            web.route('GET', '/api/tree/src', self.ls_src),
            web.route('GET', '/api/tree/run', self.ls_run),
            # then serve index and all other statics
            web.route('GET', '/', self.index),
            web.static('/', FRONTEND_LOCAL_DIR),
        ])
        self._runner = web.AppRunner(self._app)

    #
    # routes
    #
    async def index(self, _: web.Request) -> web.FileResponse:
        return web.FileResponse(ENTRY_POINT)

    async def ls_src(self, _) -> web.Response:
        tree = scan_for_st_recursive(self._path)
        return web.json_response(tree,
                                 dumps=lambda s: json.dumps(s, indent=4))

    async def ls_run(self, _) -> web.Response:
        tree = scan_for_run_recursive(self._path)
        return web.json_response(tree,
                                 dumps=lambda s: json.dumps(s, indent=4))

    #
    # error handling
    #

    @web.middleware
    async def on_request_error(self,
                               request: web.Request,
                               handler: Handler) -> web.StreamResponse:
        try:
            return await handler(request)
        except web.HTTPNotFound as e404:
            # FileNotFoundError
            Log.critical(Memo(e404).by('Middleware'))
            return web.FileResponse(ENTRY_POINT)
        except Exception as e:
            # any other errors
            Log.exception(e)
            return web.FileResponse(ENTRY_POINT)

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
        # aiohttp does not support CORS by default
        click.echo(f'Serving {self._path} at http://{self._host}:{self._port}')
        await self._runner.setup()
        site = web.TCPSite(self._runner, host=self._host, port=self._port)
        await site.start()
        await Future()  # run forever

    @override
    def run(self) -> None:
        asyncio.run(self.serve())
