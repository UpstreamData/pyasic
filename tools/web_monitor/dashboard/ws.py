import asyncio
import datetime

import websockets.exceptions
from fastapi import WebSocket, WebSocketDisconnect, APIRouter

from tools.web_monitor.func import get_current_miner_list
from tools.web_monitor._settings.func import (  # noqa - Ignore access to _module
    get_current_settings,
)
from tools.web_monitor.dashboard.func import get_miner_data_dashboard


router = APIRouter()


@router.websocket("/dashboard/ws")
async def dashboard_websocket(websocket: WebSocket):
    await websocket.accept()
    graph_sleep_time = get_current_settings()["graph_data_sleep_time"]
    try:
        while True:
            miners = get_current_miner_list()
            all_miner_data = []
            data_gen = asyncio.as_completed(
                [get_miner_data_dashboard(miner_ip) for miner_ip in miners]
            )
            for all_data in data_gen:
                data_point = await all_data
                all_miner_data.append(data_point)
            all_miner_data.sort(key=lambda x: x["ip"])
            await websocket.send_json(
                {
                    "datetime": datetime.datetime.now().isoformat(),
                    "miners": all_miner_data,
                }
            )
            await asyncio.sleep(graph_sleep_time)
    except WebSocketDisconnect:
        print("Websocket disconnected.")
        pass
    except websockets.exceptions.ConnectionClosedOK:
        pass
