import asyncio
import datetime

import websockets.exceptions
from fastapi import WebSocket, WebSocketDisconnect, APIRouter

from tools.web_monitor.miner_factory import miner_factory
from tools.web_monitor.settings.func import get_current_settings


router = APIRouter()


@router.websocket("/{miner_ip}/ws")
async def miner_websocket(websocket: WebSocket, miner_ip):
    await websocket.accept()
    settings = get_current_settings()
    miner_identify_timeout = settings["miner_identify_timeout"]
    miner_data_timeout = settings["miner_data_timeout"]

    try:
        while True:
            try:
                cur_miner = await asyncio.wait_for(
                    miner_factory.get_miner(str(miner_ip)),
                    miner_identify_timeout
                )

                data = await asyncio.wait_for(
                    cur_miner.api.multicommand("summary", "fans", "stats"),
                    miner_data_timeout
                )
                print(data)
                miner_model = await cur_miner.get_model()

                miner_summary = None
                miner_fans = None
                if "summary" in data.keys():
                    miner_summary = data["summary"][0]
                elif "SUMMARY" in data.keys():
                    miner_summary = data
                    miner_fans = {"FANS": []}
                    for item in ["Fan Speed In", "Fan Speed Out"]:
                        if item in miner_summary["SUMMARY"][0].keys():
                            miner_fans["FANS"].append(
                                {"RPM": miner_summary["SUMMARY"][0][item]})

                if "fans" in data.keys():
                    miner_fans = data["fans"][0]

                if "stats" in data.keys() and not miner_fans:
                    miner_stats = data["stats"][0]
                    miner_fans = {"FANS": []}
                    for item in ["fan1", "fan2", "fan3", "fan4"]:
                        if item in miner_stats["STATS"][1].keys():
                            miner_fans["FANS"].append(
                                {"RPM": miner_stats["STATS"][1][item]})

                if miner_summary:
                    if 'MHS av' in miner_summary['SUMMARY'][0].keys():
                        hashrate = float(format(
                            round(
                                miner_summary['SUMMARY'][0]['MHS av'] / 1000000,
                                2), ".2f"))
                    elif 'GHS av' in miner_summary['SUMMARY'][0].keys():
                        hashrate = float(format(
                            round(miner_summary['SUMMARY'][0]['GHS av'] / 1000,
                                  2),
                            ".2f"))
                    else:
                        hashrate = 0
                else:
                    hashrate = 0

                fan_speeds = []
                if miner_fans:
                    for fan in miner_fans["FANS"]:
                        fan_speeds.append(fan["RPM"])

                while len(fan_speeds) < 4:
                    fan_speeds.append(0)

                data = {"hashrate": hashrate,
                        "fans": fan_speeds,
                        "datetime": datetime.datetime.now().isoformat(),
                        "model": miner_model}
                await websocket.send_json(data)
                print(data)
                await asyncio.sleep(settings["graph_data_sleep_time"])
            except asyncio.exceptions.TimeoutError:
                data = {"error": "The miner is not responding."}
                await websocket.send_json(data)
                await asyncio.sleep(.5)
            except KeyError as e:
                print(e)
                data = {
                    "error": "The miner returned unusable/unsupported data."}
                await websocket.send_json(data)
                await asyncio.sleep(.5)
    except WebSocketDisconnect:
        print("Websocket disconnected.")
    except websockets.exceptions.ConnectionClosedOK:
        pass
