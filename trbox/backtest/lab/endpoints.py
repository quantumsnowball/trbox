import asyncio
import json
from sqlite3 import DatabaseError

import aiohttp
import aiosqlite
from aiohttp import web

from trbox.common.types import WebSocketMessage
from trbox.common.utils import read_sql_async

routes = web.RouteTableDef()

#
# source
#


@routes.get('/api/source/{path:.+}')
async def get_source(request: web.Request) -> web.Response:
    path = request.match_info['path']
    with open(f'{path}') as f:
        t = f.read()
        return web.Response(text=t)


@routes.get('/api/run/init/{path:.+}')
async def run_source(request: web.Request) -> web.Response:
    path = request.match_info['path']
    return web.json_response([dict(type='stdout',
                                   text=f'executing `{path}`\n'), ])


@routes.get('/api/run/output/{path:.+}')
async def run_source_output(request: web.Request) -> web.WebSocketResponse:
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

#
# result
#


@routes.get('/api/result/{path:.+}/meta')
async def get_result_meta(request: web.Request) -> web.Response:
    path = request.match_info['path']
    async with aiosqlite.connect(f'{path}/db.sqlite') as db:
        result = await db.execute('SELECT json FROM meta')
        row = await result.fetchone()
        meta = row[0] if row else '{}'
        return web.json_response(text=meta)


@routes.get('/api/result/{path:.+}/source')
async def get_result_source(request: web.Request) -> web.Response:
    path = request.match_info['path']
    with open(f'{path}/source.py') as f:
        t = f.read()
        return web.Response(text=t)


@routes.get('/api/result/{path:.+}/metrics')
async def get_result_metrics(request: web.Request) -> web.Response:
    path = request.match_info['path']
    try:
        sort = request.query['sort'].upper()
        order = request.query['order'].upper()
        df = await read_sql_async(f'SELECT * FROM metrics ORDER BY {sort} {order}',
                                  f'{path}/db.sqlite')
    except (KeyError, DatabaseError, ):
        df = await read_sql_async(f'SELECT * FROM metrics',
                                  f'{path}/db.sqlite')
    return web.json_response(df, dumps=lambda df: str(df.to_json(orient='split',
                                                                 indent=4)))


@routes.get('/api/result/{path:.+}/equity')
async def get_result_equity(request: web.Request) -> web.Response:
    path = request.match_info['path']
    df = await read_sql_async('SELECT * from equity',
                              f'{path}/db.sqlite',)
    df = df.set_index('index')
    return web.json_response(df, dumps=lambda df: str(df.to_json(date_format='iso',
                                                                 orient='columns',
                                                                 indent=4)))


@routes.get('/api/result/{path:.+}/trades')
async def get_result_trades(request: web.Request) -> web.Response:
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


@routes.get('/api/result/{path:.+}/stats')
async def get_result_stats(request: web.Request) -> web.Response:
    path = request.match_info['path']
    strategy = request.query['strategy']
    async with aiosqlite.connect(f'{path}/db.sqlite') as db:
        result = await db.execute('SELECT json FROM stats WHERE name=?', (strategy, ))
        row = await result.fetchone()
        stats = row[0] if row else '{}'
        return web.json_response(text=stats)


@routes.get('/api/result/{path:.+}/marks')
async def get_result_marks(request: web.Request) -> web.Response:
    path = request.match_info['path']
    strategy = request.query['strategy']
    name = request.query['name']
    df = await read_sql_async('SELECT timestamp,value FROM marks WHERE strategy=? AND name=?',
                              f'{path}/db.sqlite',
                              params=(strategy, name, ))
    return web.json_response(df, dumps=lambda df: str(df.to_json(date_format='iso',
                                                                 orient='values',
                                                                 indent=4)))
