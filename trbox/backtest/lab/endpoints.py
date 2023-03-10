from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/api/source/{path:.+}')
async def get_source(request: web.Request) -> web.Response:
    path = request.match_info['path']
    with open(f'{path}') as f:
        t = f.read()
        return web.Response(text=t)
