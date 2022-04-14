from fastapi import FastAPI, WebSocket, Request
from fastapi.websockets import WebSocketDisconnect
import asyncio
from fastapi.staticfiles import StaticFiles

import uvicorn
import os
from fastapi.templating import Jinja2Templates

from tools.web_testbench._network import miner_network
from tools.web_testbench.feeds import update_installer_files
from miners.miner_factory import MinerFactory

app = FastAPI()

app.mount(
    "/public",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "public")),
    name="public",
)

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

miner_data = {
    "IP": "192.168.1.10",
    "Light": "show",
    "Fans": {
        "fan_0": {"RPM": 4620},
        "fan_1": {"RPM": 4560},
        "fan_2": {"RPM": 0},
        "fan_3": {"RPM": 0},
    },
    "HR": {"board_6": {"HR": 4.85}, "board_7": {"HR": 0.0}, "board_8": {"HR": 0.81}},
    "Temps": {
        "board_6": {"Board": 85.6875, "Chip": 93.0},
        "board_7": {"Board": 0.0, "Chip": 0.0},
        "board_8": {"Board": 0.0, "Chip": 0.0},
    },
}


class ConnectionManager:
    _instance = None
    _connections = []

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        miners = []
        for host in miner_network.hosts():
            if host in MinerFactory().miners.keys():
                miners.append(
                    {
                        "IP": str(host),
                        "Light_On": await MinerFactory().miners[host].get_light(),
                    }
                )
            else:
                miners.append({"IP": str(host), "Light_On": None})
        await websocket.send_json({"miners": miners})
        ConnectionManager._connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        print("Disconnected")
        ConnectionManager._connections.remove(websocket)

    async def broadcast_json(self, data: dict):
        for connection in ConnectionManager._connections:
            try:
                await connection.send_json(data)
            except:
                self.disconnect(connection)


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await ConnectionManager().connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if "IP" in data.keys():
                print(data)
                miner = await MinerFactory().get_miner(data["IP"])
                if data["Data"] == "unlight":
                    miner.fault_light_off()
                if data["Data"] == "light":
                    miner.fault_light_on()
    except WebSocketDisconnect:
        ConnectionManager().disconnect(websocket)
    except RuntimeError:
        ConnectionManager().disconnect(websocket)


@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@app.on_event("startup")
async def update_installer():
    await update_installer_files()


@app.on_event("startup")
def start_monitor():
    asyncio.create_task(monitor())


async def monitor():
    i = 0
    while True:
        await ConnectionManager().broadcast_json(
            {"IP": "192.168.1.11", "text": f"hello - {i}\n"}
        )
        await asyncio.sleep(5)
        await ConnectionManager().broadcast_json(miner_data)
        i += 1


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=80)
