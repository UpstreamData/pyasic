import json
import ipaddress
import datetime
import os
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
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cur_miners": get_current_miner_list()
    })


@app.get("/scan")
def scan(request: Request):
    return templates.TemplateResponse("scan.html", {
        "request": request,
        "cur_miners": get_current_miner_list()
    })


@app.get("/miner")
def miner(request: Request, miner_ip):
    return get_miner


@app.websocket("/miner/{miner_ip}/ws")
async def miner_websocket(websocket: WebSocket, miner_ip):
    await websocket.accept()
    try:
        while True:
            try:
                cur_miner = await asyncio.wait_for(miner_factory.get_miner(str(miner_ip)), 5)

                data = await asyncio.wait_for(cur_miner.api.multicommand("summary", "fans", "stats"), 5)

                miner_summary = None
                miner_stats = None
                miner_fans = None
                if "summary" in data.keys():
                    miner_summary = data["summary"][0]
                elif "SUMMARY" in data.keys():
                    miner_summary = data
                    miner_fans = {"FANS": []}
                    for item in ["Fan Speed In", "Fan Speed Out"]:
                        if item in miner_summary["SUMMARY"][0].keys():
                            miner_fans["FANS"].append({"RPM": miner_summary["SUMMARY"][0][item]})

                if "fans" in data.keys():
                    miner_fans = data["fans"][0]

                if "stats" in data.keys():
                    miner_stats = data["stats"][0]
                    miner_fans = {"FANS": []}
                    for item in ["fan1", "fan2", "fan3", "fan4"]:
                        if item in miner_stats["STATS"][1].keys():
                            miner_fans["FANS"].append({"RPM": miner_stats["STATS"][1][item]})


                if miner_summary:
                    if 'MHS av' in miner_summary['SUMMARY'][0].keys():
                        hashrate = format(
                            round(miner_summary['SUMMARY'][0]['MHS av'] / 1000000,
                                  2), ".2f")
                    elif 'GHS av' in miner_summary['SUMMARY'][0].keys():
                        hashrate = format(
                            round(miner_summary['SUMMARY'][0]['GHS av'] / 1000, 2),
                            ".2f")
                    else:
                        hashrate = 0
                else:
                    hashrate = 0

                fan_speeds = []

                if miner_fans:
                    for fan in miner_fans["FANS"]:
                        fan_speeds.append(fan["RPM"])

                while len(fan_speeds) < 5:
                    fan_speeds.append(0)


                data = {"hashrate": hashrate,
                        "fans": fan_speeds,
                        "datetime": datetime.datetime.now().isoformat()}
                await websocket.send_json(data)
                await asyncio.sleep(5)
            except asyncio.exceptions.TimeoutError:
                data = {"error": "The miner is not responding."}
                await websocket.send_json(data)
                await asyncio.sleep(.5)
            except KeyError as e:
                print(e)
                data = {"error": "The miner returned incorrect data."}
                await websocket.send_json(data)
                await asyncio.sleep(.5)
    except WebSocketDisconnect:
        print("Websocket disconnected.")
        pass


@app.get("/miner/{miner_ip}")
def get_miner(request: Request, miner_ip):
    return templates.TemplateResponse("miner.html", {
        "request": request,
        "cur_miners": get_current_miner_list(),
        "miner": miner_ip
    })


def get_current_miner_list():
    cur_miners = []
    if os.path.exists(os.path.join(os.getcwd(), "miner_list.txt")):
        with open(os.path.join(os.getcwd(), "miner_list.txt")) as file:
            for line in file.readlines():
                cur_miners.append(line.strip())
    cur_miners = sorted(cur_miners, key=lambda x: ipaddress.ip_address(x))
    return cur_miners


@app.post("/scan/add_miners")
async def add_miners_scan(request: Request):
    miners = await request.json()
    with open("miner_list.txt", "a+") as file:
        for miner in miners["miners"]:
            file.write(miner + "\n")
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
    cur_miners = get_current_miner_list()
    try:
        if "/" in network_ip:
            network_ip, network_subnet = network_ip.split("/")
            network = MinerNetwork(network_ip, mask=network_subnet)
        else:
            network = MinerNetwork(network_ip)
        miner_generator = network.scan_network_generator()
        miners = []
        async for miner in miner_generator:
            if miner and str(miner) not in cur_miners:
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
