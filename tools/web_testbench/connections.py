from fastapi import WebSocket

from miners.miner_factory import MinerFactory
from tools.web_testbench._network import miner_network


class ConnectionManager:
    _instance = None
    _connections = []
    lit_miners = []

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        miners = []
        print(ConnectionManager.lit_miners)
        for host in miner_network.hosts():
            if str(host) in ConnectionManager.lit_miners:
                miners.append(
                    {
                        "IP": str(host),
                        "Light_On": True,
                    }
                )
            else:
                miners.append({"IP": str(host), "Light_On": False})
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
