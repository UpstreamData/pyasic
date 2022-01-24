import asyncio
import ipaddress
import warnings

from tools.bad_board_util.func.ui import update_ui_with_data, update_prog_bar, set_progress_bar_len
from tools.bad_board_util.layout import window
from tools.bad_board_util.miner_factory import miner_factory


async def scan_network(network):
    await update_ui_with_data("status", "Scanning")
    await update_ui_with_data("ip_count", "")
    window["ip_table"].update([])
    network_size = len(network)
    miner_generator = network.scan_network_generator()
    await set_progress_bar_len(2 * network_size)
    progress_bar_len = 0
    asyncio.create_task(update_prog_bar(progress_bar_len))
    miners = []
    async for miner in miner_generator:
        if miner:
            miners.append(miner)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    progress_bar_len += network_size - len(miners)
    asyncio.create_task(update_prog_bar(progress_bar_len))
    get_miner_genenerator = miner_factory.get_miner_generator(miners)
    all_miners = []
    async for found_miner in get_miner_genenerator:
        all_miners.append(found_miner)
        all_miners.sort(key=lambda x: x.ip)
        window["ip_table"].update([[str(miner.ip)] for miner in all_miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("ip_count", str(len(all_miners)))
    await update_ui_with_data("status", "")


async def refresh_data(ip_list: list):
    await update_ui_with_data("status", "Getting Data")
    ips = [ipaddress.ip_address(ip) for ip in ip_list]
    if len(ips) == 0:
        ips = [ipaddress.ip_address(ip) for ip in [item[0] for item in window["ip_table"].Values]]
    await set_progress_bar_len(len(ips))
    progress_bar_len = 0
    asyncio.create_task(update_prog_bar(progress_bar_len))
    reset_table_values = []
    for item in window["ip_table"].Values:
        if item[0] in ip_list:
            reset_table_values.append([item[0]])
        else:
            reset_table_values.append(item)
    window["ip_table"].update(reset_table_values)
    progress_bar_len = 0
    data_gen = asyncio.as_completed([get_formatted_data(miner) for miner in ips])
    ip_table_data = window["ip_table"].Values
    ordered_all_ips = [item[0] for item in ip_table_data]
    for all_data in data_gen:
        data_point = await all_data
        if data_point["IP"] in ordered_all_ips:
            ip_table_index = ordered_all_ips.index(data_point["IP"])
            board_6 = " ".join([chain["chip_status"] for chain in data_point["data"][6]]).replace("o", "•")
            board_7 = " ".join([chain["chip_status"] for chain in data_point["data"][7]]).replace("o", "•")
            board_8 = " ".join([chain["chip_status"] for chain in data_point["data"][8]]).replace("o", "•")
            data = [
                data_point["IP"],
                data_point["model"],
                board_6,
                board_7,
                board_8
            ]
            ip_table_data[ip_table_index] = data
            window["ip_table"].update(ip_table_data)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("status", "")


async def scan_and_get_data(network):
    await update_ui_with_data("status", "Scanning")
    await update_ui_with_data("ip_count", "")
    await update_ui_with_data("ip_table", [])
    network_size = len(network)
    miner_generator = network.scan_network_generator()
    await set_progress_bar_len(3 * network_size)
    progress_bar_len = 0
    miners = []
    async for miner in miner_generator:
        if miner:
            miners.append(miner)
            # can output "Identifying" for each found item, but it gets a bit cluttered
            # and could possibly be confusing for the end user because of timing on
            # adding the IPs
            # window["ip_table"].update([["Identifying..."] for miner in miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    progress_bar_len += network_size - len(miners)
    asyncio.create_task(update_prog_bar(progress_bar_len))
    get_miner_genenerator = miner_factory.get_miner_generator(miners)
    all_miners = []
    async for found_miner in get_miner_genenerator:
        all_miners.append(found_miner)
        all_miners.sort(key=lambda x: x.ip)
        window["ip_table"].update([[str(miner.ip)] for miner in all_miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("ip_count", str(len(all_miners)))
    data_gen = asyncio.as_completed([get_formatted_data(miner) for miner in miners])
    ip_table_data = window["ip_table"].Values
    ordered_all_ips = [item[0] for item in ip_table_data]
    progress_bar_len += (network_size - len(miners))
    asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("status", "Getting Data")
    for all_data in data_gen:
        data_point = await all_data
        if data_point["IP"] in ordered_all_ips:
            ip_table_index = ordered_all_ips.index(data_point["IP"])
            board_6 = " ".join([chain["chip_status"] for chain in data_point["data"][6]]).replace("o", "•")
            board_7 = " ".join([chain["chip_status"] for chain in data_point["data"][7]]).replace("o", "•")
            board_8 = " ".join([chain["chip_status"] for chain in data_point["data"][8]]).replace("o", "•")
            data = [
                data_point["IP"],
                data_point["model"],
                board_6,
                board_7,
                board_8
            ]
            ip_table_data[ip_table_index] = data
            window["ip_table"].update(ip_table_data)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("status", "")


async def get_formatted_data(ip: ipaddress.ip_address):
    miner = await miner_factory.get_miner(ip)
    model = await miner.get_model()
    warnings.filterwarnings('ignore')
    board_data = await miner.get_board_info()
    data = {"IP": str(ip), "model": model, "data": board_data}
    return data
