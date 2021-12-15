import asyncio
import sys

from cfg_util.layout import window
from cfg_util.func import scan_network, sort_data, send_config, miner_light, get_data, export_config_file, \
    generate_config, import_config, import_iplist, import_config_file, export_iplist

from network import MinerNetwork


async def ui():
    while True:
        event, value = window.read(timeout=10)
        if event in (None, 'Close'):
            sys.exit()
        if event == 'scan':
            if len(value['miner_network'].split("/")) > 1:
                network = value['miner_network'].split("/")
                miner_network = MinerNetwork(ip_addr=network[0], mask=network[1])
            else:
                miner_network = MinerNetwork(value['miner_network'])
            asyncio.create_task(scan_network(miner_network))
        if event == 'select_all_ips':
            if value['ip_list'] == window['ip_list'].Values:
                window['ip_list'].set_value([])
            else:
                window['ip_list'].set_value(window['ip_list'].Values)
        if event == 'import_config':
            if 2 > len(value['ip_list']) > 0:
                asyncio.create_task(import_config(value['ip_list']))
        if event == 'light':
            asyncio.create_task(miner_light(value['ip_list']))
        if event == "import_iplist":
            asyncio.create_task(import_iplist(value["file_iplist"]))
        if event == "export_iplist":
            asyncio.create_task(export_iplist(value["file_iplist"], value['ip_list']))
        if event == "send_config":
            asyncio.create_task(send_config(value['ip_list'], value['config']))
        if event == "import_file_config":
            asyncio.create_task(import_config_file(value['file_config']))
        if event == "export_file_config":
            asyncio.create_task(export_config_file(value['file_config'], value["config"]))
        if event == "get_data":
            asyncio.create_task(get_data(value['ip_list']))
        if event == "generate_config":
            asyncio.create_task(generate_config())
        if event == "sort_data_ip":
            asyncio.create_task(sort_data('ip'))
        if event == "sort_data_hr":
            asyncio.create_task(sort_data('hr'))
        if event == "sort_data_user":
            asyncio.create_task(sort_data(3))
        if event == "sort_data_w":
            asyncio.create_task(sort_data('wattage'))
        if event == "__TIMEOUT__":
            await asyncio.sleep(0)
