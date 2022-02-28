import json
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from tools.web_monitor.miner_factory import miner_factory
from network import MinerNetwork

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/scan")
def scan(request: Request):
    return templates.TemplateResponse("scan.html", {"request": request})


@app.post("/scan/add_miners")
async def add_miners_scan(request: Request):
    print(await request.json())
    return scan


@app.websocket("/scan/ws")
async def websocket_scan(websocket: WebSocket):
    await websocket.accept()
    cur_task = None
    try:
        while True:
            ws_data = await websocket.receive_text()
            if "-Cancel-" in ws_data:
                if cur_task:
                    cur_task.cancel()
                    try:
                        await cur_task
                    except asyncio.CancelledError:
                        cur_task = None
                await websocket.send_text("Cancelled")
            else:
                cur_task = asyncio.create_task(do_websocket_scan(websocket, ws_data))
            if cur_task and cur_task.done():
                cur_task = None
    except WebSocketDisconnect:
        print("Websocket disconnected.")
        pass


async def do_websocket_scan(websocket: WebSocket, network_ip: str):
    try:
        if "/" in network_ip:
            network_ip, network_subnet = network_ip.split("/")
            network = MinerNetwork(network_ip, mask=network_subnet)
        else:
            network = MinerNetwork(network_ip)
        miner_generator = network.scan_network_generator()
        miners = []
        async for miner in miner_generator:
            if miner:
                miners.append(miner)

        get_miner_genenerator = miner_factory.get_miner_generator(miners)
        all_miners = []
        async for found_miner in get_miner_genenerator:
            all_miners.append(
                {"ip": found_miner.ip, "model": await found_miner.get_model()})
            all_miners.sort(key=lambda x: x["ip"])
            send_miners = []
            for miner in all_miners:
                send_miners.append(
                    {"ip": str(miner["ip"]), "model": miner["model"]})
            await websocket.send_json(send_miners)
        await websocket.send_text("Done")
    except asyncio.CancelledError:
        raise

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=80)
