from aiohttp import web
import aiohttp
import os
TARGET_BOT_URL = "http://alpha.aspectsystems.nl:25686"

async def handle_forward(request):
    path = request.path
    query_string = request.query_string
    
    destination_url = f"{TARGET_BOT_URL}{path}"
    if query_string:
        destination_url += f"?{query_string}"
        
    print(f"Forwarding incoming request to: {destination_url}")

    try:
        async with request.app['http_session'].request(
            method=request.method,
            url=destination_url,
            headers=request.headers,
            data=await request.read() if request.can_read_body else None
        ) as response:
            
            body = await response.read()
            return web.Response(body=body, status=response.status, headers=response.headers)
            
    except Exception as e:
        print(f"Error trying to forward to bot server: {e}")
        return web.Response(text=f"Forwarder error: Could not reach back-end server.", status=502)

async def start_server():
    app = web.Application()
    
    app['http_session'] = aiohttp.ClientSession()
    
    async def on_cleanup(app):
        await app['http_session'].close()
    app.on_cleanup.append(on_cleanup)
    app.router.add_route('*', '/{tail:.*}', handle_forward)
    
    return app

port = int(os.environ.get("PORT", 8080))

if __name__ == "__main__":
    app = web.Application()
    web.run_app(start_server(), host="0.0.0.0", port=port)
