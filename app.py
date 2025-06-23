import uvicorn
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
from urllib.parse import urlparse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request

# read RFC 7230, Section 5.3.2

class AbsoluteFormMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        raw_path = request.scope["path"]

        # Detect and parse absolute-form (e.g., "http://host/path")
        print("Request Received: ", raw_path)
        if raw_path.startswith("http://") or raw_path.startswith("https://"):
            parsed = urlparse(raw_path)
            request.scope["path"] = parsed.path or "/"
            request.scope["root_path"] = ""
            request.scope["query_string"] = parsed.query.encode()

        return await call_next(request)

app = FastAPI()
app.add_middleware(AbsoluteFormMiddleware)

@app.get("/")
def root():
    return {"message": "Hello from root!"}

@app.get("/hello")
def hello():
    return {"message": "Hello from /hello endpoint!"}


# === Configuration ===
USE_TLS = True               # Set to True for HTTPS
HOST = "0.0.0.0"
PORT = 8080 if not USE_TLS else 8443

async def main():
    config = Config()
    config.bind = [f"{HOST}:{PORT}"]

    if USE_TLS:
        config.certfile = "cert.pem"
        config.keyfile = "key.pem"
        config.alpn_protocols = ["http/1.1"] #"h2", "http/1.1"

    await serve(app, config)


if __name__ == "__main__":

    if USE_TLS:
        asyncio.run(main())
    else:
        uvicorn_kwargs = {
            "app": "app:app",
            "host": HOST,
            "port": PORT,
        }   

        uvicorn.run(**uvicorn_kwargs)
