import uvicorn
import asyncio
import multiprocessing
from hypercorn.asyncio import serve
from hypercorn.config import Config
from urllib.parse import urlparse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, File, UploadFile  # Removed unused Form import
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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
# app.add_middleware(AbsoluteFormMiddleware)

@app.get("/")
def root():
    return {"message": "Hello from root!"}

@app.get("/hello")
def hello():
    return {"message": "Hello from /hello endpoint!"}

class HelloRequest(BaseModel):
    name: str
    age: int

@app.post("/hello")
def hello_post(body: HelloRequest):
    return {"message": f"Hello {body.name}, you are {body.age} years old!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    # For demonstration, just return file info and description
    return JSONResponse({
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content)
    })


# === Configuration ===
HOST = "0.0.0.0"
HTTP_PORT = 8082
HTTPS_PORT = 8443

async def run_https():
    config = Config()
    config.bind = [f"{HOST}:{HTTPS_PORT}"]
    config.certfile = "cert.pem"
    config.keyfile = "key.pem"
    config.alpn_protocols = ["http/1.1"]
    await serve(app, config)

def run_http():
    uvicorn.run("app:app", host=HOST, port=HTTP_PORT)

if __name__ == "__main__":
    # Start HTTP server in a separate process
    http_proc = multiprocessing.Process(target=run_http)
    http_proc.start()

    # Start HTTPS server in the main process (async)
    asyncio.run(run_https())

    http_proc.join()
