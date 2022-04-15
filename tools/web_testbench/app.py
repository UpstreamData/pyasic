from fastapi import FastAPI, WebSocket, Request
from fastapi.websockets import WebSocketDisconnect
import asyncio
from fastapi.staticfiles import StaticFiles

import uvicorn
import os
from fastapi.templating import Jinja2Templates

from tools.web_testbench.feeds import update_installer_files
from miners.miner_factory import MinerFactory
from tools.web_testbench.connections import ConnectionManager
from tools.web_testbench._miners import TestbenchMiner
from tools.web_testbench._network import miner_network

app = FastAPI()

app.mount(
    "/public",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "public")),
    name="public",
)

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await ConnectionManager().connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if "IP" in data.keys():
                miner = await MinerFactory().get_miner(data["IP"])
                try:
                    if data["Data"] == "unlight":
                        if data["IP"] in ConnectionManager.lit_miners:
                            ConnectionManager.lit_miners.remove(data["IP"])
                        await miner.fault_light_off()
                    if data["Data"] == "light":
                        if data["IP"] not in ConnectionManager().lit_miners:
                            ConnectionManager.lit_miners.append(data["IP"])
                        await miner.fault_light_on()
                except AttributeError:
                    await ConnectionManager().broadcast_json({"IP": data["IP"], "text": "Fault light command failed, miner is not running BraiinsOS."})
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
def start_install():
    asyncio.create_task(install())


async def install():
    for host in miner_network.hosts():
        miner = TestbenchMiner(host)
        asyncio.create_task(miner.install_loop())


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=80)
