from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

import uvicorn
import os
from fastapi.templating import Jinja2Templates


app = FastAPI()

app.mount("/public", StaticFiles(
    directory=os.path.join(os.path.dirname(__file__), "public")), name="public")

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates"))


class ConnectionManager:
    _instance = None

    def __init__(self):
        self.connections = []

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(
                ConnectionManager,
                cls
            ).__new__(cls)
        return cls._instance

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast_json(self, data: str):
        for connection in self.connections:
            await connection.json(data)


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await ConnectionManager().connect(websocket)


@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
    })


if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=80)
