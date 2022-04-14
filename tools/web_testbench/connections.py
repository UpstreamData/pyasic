from fastapi import WebSocket

from miners.miner_factory import MinerFactory
from tools.web_testbench._network import miner_network


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
            except Exception as e:
                self.disconnect(connection)
