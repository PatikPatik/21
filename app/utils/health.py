from aiohttp import web

async def add_health_endpoint(aiohttp_app: web.Application) -> None:
    async def healthz(_):
        return web.Response(text="ok")
    aiohttp_app.add_routes([web.get("/healthz", healthz)])
