import asyncio
import sys
import PySimpleGUI as sg

from cfg_util.layout import window, generate_config_layout
from cfg_util.func.miners import scan_network, send_config, miner_light, get_data, generate_config, import_config
from cfg_util.func.files import import_iplist, import_config_file, export_iplist, export_config_file
from cfg_util.func.ui import sort_data

from network import MinerNetwork

import webbrowser


async def ui():
    while True:
        event, value = window.read(timeout=10)
        if event in (None, 'Close', sg.WIN_CLOSED):
            sys.exit()
        if isinstance(event, tuple):
            if len(window["ip_table"].Values) > 0:
                if event[0] == 'ip_table':
                    if event[2][0] == -1:
                        await sort_data(event[2][1])
        if event == 'open_in_web':
            for row in value["ip_table"]:
                webbrowser.open("http://" + window["ip_table"].Values[row][0])
        if event == 'scan':
            if len(value['miner_network'].split("/")) > 1:
                network = value['miner_network'].split("/")
                miner_network = MinerNetwork(ip_addr=network[0], mask=network[1])
            else:
                miner_network = MinerNetwork(value['miner_network'])
            asyncio.create_task(scan_network(miner_network))
        if event == 'select_all_ips':
            if len(value["ip_table"]) == len(window["ip_table"].Values):
                window["ip_table"].update(select_rows=())
            else:
                window["ip_table"].update(select_rows=([row for row in range(len(window["ip_table"].Values))]))
        if event == 'import_config':
            if 2 > len(value['ip_table']) > 0:
                asyncio.create_task(import_config(value['ip_table']))
        if event == 'light':
            asyncio.create_task(miner_light([window['ip_table'].Values[item][0] for item in value['ip_table']]))
        if event == "import_iplist":
            asyncio.create_task(import_iplist(value["file_iplist"]))
        if event == "export_iplist":
            asyncio.create_task(export_iplist(value["file_iplist"], [window['ip_table'].Values[item][0] for item in value['ip_table']]))
        if event == "send_config":
            asyncio.create_task(send_config([window['ip_table'].Values[item][0] for item in value['ip_table']], value['config']))
        if event == "import_file_config":
            asyncio.create_task(import_config_file(value['file_config']))
        if event == "export_file_config":
            asyncio.create_task(export_config_file(value['file_config'], value["config"]))
        if event == "get_data":
            asyncio.create_task(get_data([window["ip_table"].Values[item][0] for item in value["ip_table"]]))
        if event == "generate_config":
            await generate_config_ui()
        if event == "__TIMEOUT__":
            await asyncio.sleep(0)


async def generate_config_ui():
    generate_config_window = sg.Window("Generate Config", generate_config_layout(), modal=True)
    while True:
        event, values = generate_config_window.read()
        if event in (None, 'Close', sg.WIN_CLOSED):
            break
        if event == "generate_config_window_generate":
            if values['generate_config_window_username']:
                await generate_config(values['generate_config_window_username'],
                                      values['generate_config_window_workername'],
                                      values['generate_config_window_allow_v2'])
                generate_config_window.close()
                break
