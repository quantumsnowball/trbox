import asyncio
import os
from asyncio import Future
from pathlib import Path
from threading import Thread
from typing import Any

import click
from aiohttp import web
from aiohttp.typedefs import Handler
from binance.websocket.binance_socket_manager import json
from typing_extensions import override

from trbox.backtest.lab.endpoints import routes
from trbox.backtest.utils import Node
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 7000
DEFAULT_PATH = '.'
FRONTEND_LOCAL_DIR = Path(Path(__file__).parent,
                          '../../frontend/trbox-lab/out/')
DEFAULT_FILENAME = 'index.html'
ENTRY_POINT = Path(FRONTEND_LOCAL_DIR, DEFAULT_FILENAME)
PY_SUFFIX = '.py'
RUNDIR_PREFIX = '.result'


def scan_for_source(parent: Node,
                    *,
                    suffix: str = PY_SUFFIX,
                    prefix_excluded: str = RUNDIR_PREFIX,
                    basepath: str) -> Node:
    for m in os.scandir(basepath + parent.path):
        if m.is_dir() and not m.name.startswith(prefix_excluded):
            parent.add(scan_for_source(Node(m.name, 'folder', parent, []),
                                       basepath=basepath))
        elif m.is_file() and m.name.endswith(suffix):
            parent.add(Node(m.name, 'file', parent, []))
    return parent


def scan_for_result(parent: Node,
                    *,
                    prefix: str = RUNDIR_PREFIX,
                    basepath: str) -> Node:
    # loop through every items in path
    for m in os.scandir(basepath + parent.path):
        if m.is_dir():
            if m.name.startswith(prefix):
                # prefixed dir should contain run info
                db_path = f'{basepath}/{parent.path}/{m.name}/db.sqlite'
                if (Path(db_path).is_file()):
                    # meta.json should exist in a valid result dir
                    parent.add(scan_for_result(Node(m.name, 'folder', parent, []),
                                               basepath=basepath))
            else:
                # nested one level if is a dir, key is the dirname
                parent.add(scan_for_result(Node(m.name, 'folder', parent, []),
                                           basepath=basepath))
    return parent


class Lab(Thread):
    def __init__(self,
                 path: str,
                 *args: Any,
                 host: str,
                 port: int,
                 **kwargs: Any) -> None:
        super().__init__(*args,
                         **kwargs)
        self.name = 'Lab'
        self._path = path
        self._host = host
        self._port = port
        self._app = web.Application(middlewares=[self.on_request_error, ])
        self._app.add_routes(routes)
        self._app.add_routes([
            # match api first
            web.get('/api/tree/source', self.ls_source),
            web.get('/api/tree/result', self.ls_result),
            # then serve index and all other statics
            web.get('/', self.index),
            web.static('/', FRONTEND_LOCAL_DIR),
        ])
        self._runner = web.AppRunner(self._app)

    #
    # routes
    #
    async def index(self, _: web.Request) -> web.FileResponse:
        return web.FileResponse(ENTRY_POINT)

    async def ls_source(self, _: web.Request) -> web.Response:
        node = scan_for_source(Node('', 'folder', None, []),
                               basepath=self._path)
        return web.json_response(node.dict,
                                 dumps=lambda s: str(json.dumps(s, indent=4)))

    async def ls_result(self, _: web.Request) -> web.Response:
        node = scan_for_result(Node('', 'folder', None, []),
                               basepath=self._path)
        return web.json_response(node.dict,
                                 dumps=lambda s: str(json.dumps(s, indent=4)))

    #
    # error handling
    #

    @ web.middleware
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

    @ override
    def run(self) -> None:
        asyncio.run(self.serve())
