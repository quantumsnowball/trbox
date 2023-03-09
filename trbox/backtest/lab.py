import asyncio
import os
import shutil
from asyncio import Future
from threading import Thread
from typing import Any

import aiohttp
import aiosqlite
import click
from aiohttp import web
from aiohttp.typedefs import Handler
from binance.websocket.binance_socket_manager import json
from typing_extensions import override

from trbox.backtest.utils import Node
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import WebSocketMessage
from trbox.common.utils import read_sql_async

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
                db_path = f'{basepath}/{parent.path}/{m.name}/db.sqlite'
                if (os.path.isfile(db_path)):
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
        self._app.add_routes([
            # match api first
            web.get('/api/tree/source', self.ls_source),
            web.get('/api/tree/result', self.ls_result),
            web.get('/api/run/init/{path:.+}', self.run_source),
            web.get('/api/run/output/{path:.+}', self.run_source_output),
            web.get('/api/source/{path:.+}', self.get_source),
            web.get('/api/result/{path:.+}/meta', self.get_result_meta),
            web.get('/api/result/{path:.+}/source', self.get_result_source),
            web.get('/api/result/{path:.+}/metrics', self.get_result_metrics),
            web.get('/api/result/{path:.+}/equity', self.get_result_equity),
            web.get('/api/result/{path:.+}/trades', self.get_result_trades),
            web.get('/api/result/{path:.+}/stats', self.get_result_stats),
            web.delete('/api/operation/{path:.+}', self.delete_resource),
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

    async def get_source(self, request: web.Request) -> web.Response:
        path = request.match_info['path']
        with open(f'{path}') as f:
            t = f.read()
            return web.Response(text=t)

    async def get_result_meta(self, request: web.Request) -> web.Response:
        path = request.match_info['path']
        async with aiosqlite.connect(f'{path}/db.sqlite') as db:
            result = await db.execute('SELECT json FROM meta')
            row = await result.fetchone()
            meta = row[0] if row else '{}'
            return web.json_response(text=meta)

    async def get_result_source(self, request: web.Request) -> web.Response:
        path = request.match_info['path']
        with open(f'{path}/source.py') as f:
            t = f.read()
            return web.Response(text=t)

    async def get_result_metrics(self, request: web.Request) -> web.Response:
        path = request.match_info['path']
        df = await read_sql_async('SELECT * FROM metrics',
                                  f'{path}/db.sqlite')
        return web.json_response(df, dumps=lambda df: str(df.to_json(orient='split',
                                                                     indent=4)))

    async def get_result_stats(self, request: web.Request) -> web.Response:
        path = request.match_info['path']
        strategy = request.query['strategy']
        async with aiosqlite.connect(f'{path}/db.sqlite') as db:
            result = await db.execute('SELECT json FROM stats WHERE name=?', (strategy, ))
            row = await result.fetchone()
            stats = row[0] if row else '{}'
            return web.json_response(text=stats)

    async def get_result_equity(self, request: web.Request) -> web.Response:
        path = request.match_info['path']
        df = await read_sql_async('SELECT * from equity',
                                  f'{path}/db.sqlite',)
        df = df.set_index('index')
        return web.json_response(df, dumps=lambda df: str(df.to_json(date_format='iso',
                                                                     orient='columns',
                                                                     indent=4)))

    async def get_result_trades(self, request: web.Request) -> web.Response:
        path = request.match_info['path']
        strategy = request.query['strategy']
        df = await read_sql_async('SELECT * FROM trades WHERE Strategy=?',
                                  f'{path}/db.sqlite',
                                  params=(strategy, ))
        df = df.set_index('Date')
        df = df.drop(columns=['Strategy'])
        return web.json_response(df, dumps=lambda df: str(df.to_json(date_format='iso',
                                                                     orient='table',
                                                                     indent=4)))

    async def run_source(self, request: web.Request) -> web.Response:
        path = request.match_info['path']
        return web.json_response([dict(type='stdout',
                                       text=f'executing `{path}`\n'), ])

    async def run_source_output(self, request: web.Request) -> web.WebSocketResponse:
        path = request.match_info['path']
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        print('A client has connected')
        cmd = f'python {path}'
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        print(f'created subprocess, executing: {cmd}')

        async def listen_to_message() -> None:
            print('listening to ws message from client')
            async for raw in ws:
                print('still listening ... forever')
                if raw.type == aiohttp.WSMsgType.TEXT:
                    msg: WebSocketMessage = json.loads(raw.data)
                    if msg['type'] == 'system' and msg['text'] == 'stop':
                        print('client requested to exit')
                        proc.terminate()
                        print('terminated process')
                        return

        async def read_stdout() -> None:
            if proc.stdout:
                print('stdout is ready')
                async for line in proc.stdout:
                    await ws.send_json(dict(type='stdout',
                                            text=line.decode()))
                print('stdout has ended')
                await ws.send_json(dict(
                    type='stdout',
                    text=f'executing `{path}` finished: return code = {proc.returncode}'))
                await ws.close()
                print('ws connection closed')

        async def read_stderr() -> None:
            if proc.stderr:
                print('stderr is ready')
                async for line in proc.stderr:
                    await ws.send_json(dict(type='stderr',
                                            text=line.decode()))
                print('stderr has ended')

        await asyncio.gather(listen_to_message(),
                             read_stdout(),
                             read_stderr())

        return ws

    async def delete_resource(self, request: web.Request) -> web.Response:
        path = request.match_info['path']
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        print(f'deleted {path}')
        return web.Response()

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
