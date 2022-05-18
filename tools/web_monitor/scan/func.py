import asyncio

from fastapi import WebSocket

from network import MinerNetwork
from tools.web_monitor.func import get_current_miner_list
import ipaddress
from miners.miner_factory import MinerFactory


async def do_websocket_scan(websocket: WebSocket, network_ip: str):
    cur_miners = get_current_miner_list()
    try:
        if "/" in network_ip:
            network_ip, network_subnet = network_ip.split("/")
            network = MinerNetwork(network_ip, mask=network_subnet)
        else:
            network = MinerNetwork(network_ip)
        miner_generator = network.scan_network_generator()
        all_miners = []
        async for found_miner in miner_generator:
            if found_miner and str(found_miner.ip) not in cur_miners:
                # all_miners.append(miner_ip)

                # get_miner_generator = MinerFactory().get_miner_generator(miners)
                # async for found_miner in get_miner_generator:
                all_miners.append(
                    {"ip": found_miner.ip, "model": await found_miner.get_model()}
                )
                all_miners.sort(key=lambda x: ipaddress.ip_address(x["ip"]))
                send_miners = []
                for miner_ip in all_miners:
                    send_miners.append(
                        {"ip": str(miner_ip["ip"]), "model": miner_ip["model"]}
                    )
                await websocket.send_json(send_miners)
        await websocket.send_text("Done")
    except asyncio.CancelledError:
        raise
