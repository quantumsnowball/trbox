from sqlite3 import DatabaseError

import aiosqlite
from aiohttp import web

from trbox.common.utils import read_sql_async

routes = web.RouteTableDef()


@routes.get('/api/source/{path:.+}')
async def get_source(request: web.Request) -> web.Response:
    path = request.match_info['path']
    with open(f'{path}') as f:
        t = f.read()
        return web.Response(text=t)


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
