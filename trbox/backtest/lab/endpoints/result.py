import json
from collections import defaultdict
from sqlite3 import DatabaseError

import aiosqlite
from aiohttp import web

from trbox.common.utils import read_sql_async

routes = web.RouteTableDef()


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

    # /marks?strategy=<strategy>&name=<name>
    async def give_series() -> web.Response:
        df = await read_sql_async('SELECT timestamp,value FROM marks WHERE strategy=? AND name=?',
                                  f'{path}/db.sqlite',
                                  params=(strategy, name, ))
        return web.json_response(df, dumps=lambda df: str(df.to_json(date_format='iso',
                                                                     orient='values',
                                                                     indent=4)))

    # /marks?strategy=<?>&name=<?>&interp=<?>
    async def give_series_interp() -> web.Response:
        return web.json_response([])

    # /marks, or either only strategy or name is given
    async def give_index() -> web.Response:
        df = await read_sql_async('SELECT DISTINCT strategy,name FROM marks',
                                  f'{path}/db.sqlite',
                                  index_col=['strategy',])
        index = defaultdict(list)
        for strategy, name in df.itertuples():
            index[strategy].append(name)
        return web.json_response(index, dumps=lambda d: json.dumps(d, indent=4))

    try:
        strategy = request.query['strategy']
        name = request.query['name']
        interp = request.query.get('interp', None)
        if interp:
            return await give_series_interp()
        else:
            return await give_series()
    except (KeyError, DatabaseError, ):
        return await give_index()
