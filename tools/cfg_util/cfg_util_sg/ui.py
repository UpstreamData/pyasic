import asyncio
import sys
import PySimpleGUI as sg
import tkinter as tk

from tools.cfg_util.cfg_util_sg.layout import window, generate_config_layout, send_ssh_cmd_layout
from tools.cfg_util.cfg_util_sg.func.miners import send_config, miner_light, refresh_data, generate_config, import_config, \
    scan_and_get_data, restart_miners_backend, reboot_miners, send_miners_ssh_commands
from tools.cfg_util.cfg_util_sg.func.files import import_iplist, \
    import_config_file, export_iplist, export_config_file, export_csv
from tools.cfg_util.cfg_util_sg.func.decorators import disable_buttons
from tools.cfg_util.cfg_util_sg.func.ui import sort_data, copy_from_table, copy_from_ssh_table

from network import MinerNetwork

import webbrowser


async def ui():
    window.read(timeout=0)
    table = window["ip_table"].Widget
    table.bind("<Control-Key-c>", lambda x: copy_from_table(table))
    # left justify the hostnames
    table.column(2, anchor=tk.W)
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
            asyncio.create_task(scan_and_get_data(miner_network))
        if event == 'select_all_ips':
            if len(value["ip_table"]) == len(window["ip_table"].Values):
                window["ip_table"].update(select_rows=())
            else:
                window["ip_table"].update(select_rows=([row for row in range(len(window["ip_table"].Values))]))
        if event == 'import_config':
            if 2 > len(value['ip_table']) > 0:
                asyncio.create_task(import_config(value['ip_table']))
        if event == "restart_miner_backend":
            if len(window["ip_table"].Values) > 0:
                asyncio.create_task(restart_miners_backend([window['ip_table'].Values[item][0] for item in value['ip_table']]))
        if event == "reboot_miners":
            if len(window["ip_table"].Values) > 0:
                asyncio.create_task(reboot_miners([window['ip_table'].Values[item][0] for item in value['ip_table']]))
        if event == "send_miner_ssh_command_window":
            ips = [window['ip_table'].Values[item][0] for item in value['ip_table']]
            if len(ips) == 0:
                ips = [item[0] for item in window["ip_table"].Values]
            if not len(ips) == 0:
                await generate_ssh_cmd_ui(ips)
        if event == 'light':
            if len(window["ip_table"].Values) > 0:
                asyncio.create_task(miner_light([window['ip_table'].Values[item][0] for item in value['ip_table']]))
        if event == "import_iplist":
            asyncio.create_task(import_iplist(value["file_iplist"]))
        if event == "export_iplist":
            asyncio.create_task(export_iplist(value["file_iplist"], [window['ip_table'].Values[item][0] for item in value['ip_table']]))
        if event == "export_csv":
            asyncio.create_task(export_csv(value["file_iplist"], [window['ip_table'].Values[item] for item in value['ip_table']]))
        if event == "send_config":
            if len(window["ip_table"].Values) > 0:
                asyncio.create_task(send_config([window['ip_table'].Values[item][0] for item in value['ip_table']], value['config']))
        if event == "import_file_config":
            asyncio.create_task(import_config_file(value['file_config']))
        if event == "export_file_config":
            asyncio.create_task(export_config_file(value['file_config'], value["config"]))
        if event == "refresh_data":
            if len(window["ip_table"].Values) > 0:
                asyncio.create_task(refresh_data([window["ip_table"].Values[item][0] for item in value["ip_table"]]))
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


@disable_buttons
async def generate_ssh_cmd_ui(selected_miners: list):
    ssh_cmd_window = sg.Window("Send Command", send_ssh_cmd_layout(selected_miners), modal=True)
    ssh_cmd_window.read(timeout=0)
    table = ssh_cmd_window["ssh_cmd_table"].Widget
    table.bind("<Control-Key-c>", lambda x: copy_from_ssh_table(table))
    # left justify the results
    table.column(1, anchor=tk.W)
    while True:
        event, values = ssh_cmd_window.read(timeout=0)
        if event in (None, 'Close', sg.WIN_CLOSED):
            break
        if event == "ssh_command_window_send_cmd":
            asyncio.create_task(send_miners_ssh_commands(selected_miners, values["ssh_command_window_cmd"], ssh_cmd_window))
        if event == "__TIMEOUT__":
            await asyncio.sleep(0)
