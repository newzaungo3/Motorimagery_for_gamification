import uvicorn

async def app(scope, receive, send):
    ...

if __name__ == "__main__":
    config = uvicorn.Config("server:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.run()