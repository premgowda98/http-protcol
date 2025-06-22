from fastapi import FastAPI
import uvicorn
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config


app = FastAPI()

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
        config.alpn_protocols = ["h2", "http/1.1"] #"h2", "http/1.1"

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
