import asyncio

from tools.cfg_util.cfg_util_qt.tables import clear_tables, update_tables
from tools.cfg_util.cfg_util_qt.layout import window, update_prog_bar
from network import MinerNetwork
from miners.miner_factory import MinerFactory
from API import APIError

import warnings
import logging

progress_bar_len = 0

DEFAULT_DATA = [
    "Model",
    "Hostname",
    "Hashrate",
    "Temperature",
    "Pool User",
    "Pool 1",
    "Pool 1 User",
    "Pool 2",
    "Pool 2 User",
    "Wattage",
    "Split",
]


async def btn_all():
    table = "scan_table"
    window[table].update(
        select_rows=([row for row in range(len(window[table].Values))])
    )


async def btn_scan(scan_ip: str):
    network = MinerNetwork("192.168.1.0")
    if scan_ip:
        if "/" in scan_ip:
            ip, mask = scan_ip.split("/")
            network = MinerNetwork(ip, mask=mask)
        else:
            network = MinerNetwork(scan_ip)
    asyncio.create_task(_scan_miners(network))


async def _scan_miners(network: MinerNetwork):
    clear_tables()
    scan_generator = network.scan_network_generator()
    MinerFactory().clear_cached_miners()

    global progress_bar_len

    network_size = len(network)
    await update_prog_bar(progress_bar_len, max=(3 * network_size))

    scanned_miners = []
    async for miner in scan_generator:
        if miner:
            scanned_miners.append(miner)
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)

    progress_bar_len += network_size - len(scanned_miners)
    await update_prog_bar(progress_bar_len)

    get_miner_genenerator = MinerFactory().get_miner_generator(scanned_miners)

    resolved_miners = []
    async for found_miner in get_miner_genenerator:
        resolved_miners.append(found_miner)
        resolved_miners.sort(key=lambda x: x.ip)
        resolved_miners_data = []
        for miner in resolved_miners:
            _data = {}
            for key in DEFAULT_DATA:
                _data[key] = ""
            _data["IP"] = str(miner.ip)
            _data["Light"] = False
            update_tables([_data])
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)
    progress_bar_len += network_size - len(resolved_miners)
    await update_prog_bar(progress_bar_len)
    await _get_miners_data(resolved_miners)


async def _get_miners_data(miners: list):
    global progress_bar_len
    data_generator = asyncio.as_completed([_get_data(miner) for miner in miners])
    miner_data = [{"IP": str(miner.ip)} for miner in miners]
    for all_data in data_generator:
        data = await all_data
        for idx, item in enumerate(miner_data):
            if item["IP"] == data["IP"]:
                miner_data[idx] = data
        update_tables(miner_data)
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)


async def _get_data(miner):
    return await miner.get_data()
