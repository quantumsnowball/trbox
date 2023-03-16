import json
from collections import defaultdict
from pathlib import Path
from sqlite3 import DatabaseError

import aiosqlite
from aiohttp import web
from pandas import DataFrame, concat

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
                                  Path(path, 'db.sqlite'))
    except (KeyError, DatabaseError, ):
        df = await read_sql_async(f'SELECT * FROM metrics',
                                  Path(path, 'db.sqlite'))
    return web.json_response(df, dumps=lambda df: str(df.to_json(orient='split',
                                                                 indent=4)))


@routes.get('/api/result/{path:.+}/equity')
async def get_result_equity(request: web.Request) -> web.Response:
    path = request.match_info['path']
    df = await read_sql_async('SELECT * from equity',
                              Path(path, 'db.sqlite'),)
    df = df.set_index('index')
    return web.json_response(df, dumps=lambda df: str(df.to_json(date_format='iso',
                                                                 orient='columns',
                                                                 indent=4)))


@routes.get('/api/result/{path:.+}/trades')
async def get_result_trades(request: web.Request) -> web.Response:
    path = request.match_info['path']
    strategy = request.query['strategy']
    df = await read_sql_async('SELECT * FROM trades WHERE Strategy=?',
                              Path(path, 'db.sqlite'),
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
    # /marks?strategy=<strategy>&name=<name>
    async def give_series(path: str, strategy: str, name: str) -> web.Response:
        df = await read_sql_async('SELECT timestamp,value FROM marks WHERE strategy=? AND name=?',
                                  Path(path, 'db.sqlite'),
                                  params=(strategy, name, ))
        return web.json_response(df, dumps=lambda df: str(df.to_json(date_format='iso',
                                                                     orient='values',
                                                                     indent=4)))

    # /marks?strategy=<?>&name=<?>&interp=<?>
    async def give_series_interp(path: str, strategy: str, name: str, interp: str) -> web.Response:
        overlay_df = await read_sql_async('SELECT timestamp,value FROM marks WHERE strategy=? AND name=?',
                                          Path(path, 'db.sqlite'),
                                          params=(strategy, name, ))
        main_df = await read_sql_async('SELECT timestamp,value FROM marks WHERE strategy=? AND name=?',
                                       Path(path, 'db.sqlite'),
                                       params=(strategy, interp, ))
        # return empty if either df is empty
        if len(overlay_df) == 0 or len(main_df) == 0:
            return web.json_response([])
        #
        combined_df = (concat([overlay_df, main_df])
                       .drop_duplicates(subset='timestamp', keep='last')
                       .sort_values(by='timestamp'))
        converted_df = (combined_df.set_index('timestamp')
                        .astype(float)
                        .interpolate(method='index'))
        result_df = (converted_df.loc[overlay_df.timestamp].reset_index()
                     if converted_df is not None
                     else DataFrame([]))
        return web.json_response(result_df, dumps=lambda df: str(df.to_json(date_format='iso',
                                                                            orient='values',
                                                                            indent=4)))

    # /marks, or either only strategy or name is given
    async def give_index(path: str) -> web.Response:
        df = await read_sql_async('SELECT DISTINCT strategy,name FROM marks',
                                  Path(path, 'db.sqlite'),
                                  index_col=['strategy',])
        index = defaultdict(list)
        for strategy, name in df.itertuples():
            index[strategy].append(name)
        return web.json_response(index, dumps=lambda d: json.dumps(d, indent=4))

    path = request.match_info['path']
    try:
        strategy = request.query['strategy']
        name = request.query['name']
        interp = request.query.get('interp', None)
        if not interp:
            return await give_series(path, strategy, name)
        else:
            return await give_series_interp(path, strategy, name, interp)
    except (KeyError, DatabaseError, ):
        return await give_index(path)
