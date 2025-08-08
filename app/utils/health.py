from aiohttp import web

def make_health_app() -> web.Application:
    app = web.Application()
    async def healthz(_):
        return web.Response(text="ok")
    app.add_routes([web.get("/healthz", healthz)])
    return app
