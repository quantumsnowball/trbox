import asyncio
import json

import aiohttp
from aiohttp import web

from trbox.common.types import WebSocketMessage

routes = web.RouteTableDef()


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
