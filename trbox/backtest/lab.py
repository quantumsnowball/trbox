import os
from asyncio import Future
from threading import Thread
from typing import Any

import click
import pandas as pd
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
                source_path = f'{basepath}/{parent.path}/{m.name}/meta.json'
                metrics_path = f'{basepath}/{parent.path}/{m.name}/metrics.pkl'
                equity_path = f'{basepath}/{parent.path}/{m.name}/equity.pkl'
                if (os.path.isfile(meta_path) or
                    os.path.isfile(source_path) or
                    os.path.isfile(metrics_path) or
                        os.path.isfile(equity_path)):
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
            web.get('/api/tree/source', self.ls_source),
            web.get('/api/tree/result', self.ls_result),
            web.get('/api/run/init/{path:.+}', self.run_source),
            web.get('/api/run/output/{path:.+}', self.run_source_output),
            web.get('/api/source/{path:.+}', self.get_source),
            web.get('/api/result/{path:.+}/metrics', self.get_result_metrics),
            web.get('/api/result/{path:.+}/equity', self.get_result_equity),
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
            t = f.read()
            return web.Response(text=t)

    async def get_result_metrics(self, request) -> web.Response:
        path = request.match_info['path']
        df = pd.read_pickle(f'{path}/metrics.pkl')
        return web.json_response(df, dumps=lambda df: df.to_json(orient='split',
                                                                 indent=4))

    async def get_result_equity(self, request) -> web.Response:
        path = request.match_info['path']
        df = pd.read_pickle(f'{path}/equity.pkl')
        return web.json_response(df, dumps=lambda df: df.to_json(date_format='iso',
                                                                 orient='columns',
                                                                 indent=4))

    async def run_source(self, request) -> web.Response:
        path = request.match_info['path']
        return web.json_response([dict(type='stdout',
                                       text=f'executing {path}'), ])

    async def run_source_output(self, request) -> web.WebSocketResponse:
        path = request.match_info['path']
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        print('Something has connected')
        cmd = f'python {path}'
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        print(f'executing: {cmd}')
        if proc.stdout:
            print('stdout is ready')
            async for line in proc.stdout:
                print('.', end='', flush=True)
                await ws.send_json(dict(type='stdout',
                                        text=line.decode()))
        if proc.stderr:
            print('stderr is ready')
            async for line in proc.stderr:
                print('x', flush=True)
                await ws.send_json(dict(type='stderr',
                                        text=line.decode()))

        print('end of stdout / stderr, closing ws ...')
        # await ws.send_json(dict(type='stdout', text='finished, exiting'))
        await ws.close()
        return ws

    # async def run_ws(self, request):
    #     ws = web.WebSocketResponse()
    #     await ws.prepare(request)
    #     print('Something has connected')
    #     await ws.send_str(
    #         'Welcome to ws channel, gonna update you when stdout prints!')
    #
    #     for i in range(10):
    #         await ws.send_str(f'{i}')
    #         await asyncio.sleep(1)
    #
    #     async for msg in ws:
    #         if msg.type == aiohttp.WSMsgType.TEXT:
    #             print(msg)
    #             if msg.data == 'close':
    #                 await ws.close()
    #             else:
    #                 await ws.send_str(msg.data + '/answer')
    #         elif msg.type == aiohttp.WSMsgType.ERROR:
    #             print('ws connection closed with exception %s' %
    #                   ws.exception())
    #
    #     print('websocket connection closed')
    #
    #     return ws
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
