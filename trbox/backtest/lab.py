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

from trbox.backtest.utils import Node
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 7000
DEFAULT_PATH = '.'
FRONTEND_LOCAL_DIR = f'{os.path.dirname(__file__)}/../frontend/trbox-lab/out/'
DEFAULT_FILENAME = 'index.html'
ENTRY_POINT = f'{FRONTEND_LOCAL_DIR}{DEFAULT_FILENAME}'
PY_SUFFIX = '.py'
RUNDIR_PREFIX = '.result'


TreeDict = dict[str, Union['TreeDict', None]]


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
                meta_path = f'{basepath}/{parent.path}/{m.name}/meta.json'
                if os.path.isfile(meta_path):
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
                         name='Lab',
                         **kwargs)
        self._path = path
        self._host = host
        self._port = port
        self._app = web.Application(middlewares=[self.on_request_error, ])
        self._app.add_routes([
            # match api first
            web.route('GET', '/api/tree/source', self.ls_source),
            web.route('GET', '/api/tree/result', self.ls_result),
            web.route('GET', '/api/source/{path:.+}', self.get_source),
            web.route('GET', '/api/result/{path:.+}', self.get_result_meta),
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

    async def ls_source(self, _) -> web.Response:
        node = scan_for_source(Node('', 'folder', None, []),
                               basepath=self._path)
        return web.json_response(node.dict,
                                 dumps=lambda s: json.dumps(s, indent=4))

    async def ls_result(self, _) -> web.Response:
        node = scan_for_result(Node('', 'folder', None, []),
                               basepath=self._path)
        return web.json_response(node.dict,
                                 dumps=lambda s: json.dumps(s, indent=4))

    async def get_source(self, request) -> web.Response:
        path = request.match_info['path']
        with open(f'{path}') as f:
            d = dict(code=f.read())
            return web.json_response(d, dumps=lambda s: json.dumps(s, indent=4))

    async def get_result_meta(self, request) -> web.Response:
        path = request.match_info['path']
        with open(f'{path}/meta.json') as f:
            txt = json.load(f)
            return web.json_response(txt, dumps=lambda s: json.dumps(s, indent=4))

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

    # TODO: propose definition of a `lab` dir:
    # 1. contains a single *.py file
    # 2. can have subdir or any other files
    # TODO: to create a lab in frontend:
    # 1. cwd for a selected *.py
    # 2. copy to new subdir and copy the original *.py into it

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
