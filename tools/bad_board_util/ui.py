import asyncio
import sys
import PySimpleGUI as sg
import xlsxwriter

from tools.bad_board_util.layout import window
from tools.bad_board_util.func.miners import refresh_data, scan_and_get_data
from tools.bad_board_util.func.files import import_iplist, export_iplist, save_report
from tools.bad_board_util.func.ui import sort_data, copy_from_table, table_select_all

from network import MinerNetwork

import webbrowser


async def ui():
    window.read(timeout=0)
    table = window["ip_table"].Widget
    table.bind("<Control-Key-c>", lambda x: copy_from_table(table))
    table.bind("<Control-Key-a>", lambda x: table_select_all())
    while True:
        event, value = window.read(timeout=0)
        if event in (None, "Close", sg.WIN_CLOSED):
            sys.exit()
        if isinstance(event, tuple):
            if len(window["ip_table"].Values) > 0:
                if event[0] == "ip_table":
                    if event[2][0] == -1:
                        await sort_data(event[2][1])
        if event == "open_in_web":
            for row in value["ip_table"]:
                webbrowser.open("http://" + window["ip_table"].Values[row][0])
        if event == "scan":
            if len(value["miner_network"].split("/")) > 1:
                network = value["miner_network"].split("/")
                miner_network = MinerNetwork(ip_addr=network[0], mask=network[1])
            else:
                miner_network = MinerNetwork(value["miner_network"])
            asyncio.create_task(scan_and_get_data(miner_network))
        if event == "save_report":
            if not value["save_report"] == "":
                asyncio.create_task(save_report(value["save_report"]))
        if event == "select_all_ips":
            if len(value["ip_table"]) == len(window["ip_table"].Values):
                window["ip_table"].update(select_rows=())
            else:
                window["ip_table"].update(
                    select_rows=([row for row in range(len(window["ip_table"].Values))])
                )
        if event == "import_iplist":
            asyncio.create_task(import_iplist(value["file_iplist"]))
        if event == "export_iplist":
            asyncio.create_task(
                export_iplist(
                    value["file_iplist"],
                    [window["ip_table"].Values[item][0] for item in value["ip_table"]],
                )
            )
        if event == "refresh_data":
            asyncio.create_task(
                refresh_data(
                    [window["ip_table"].Values[item][0] for item in value["ip_table"]]
                )
            )
        if event == "__TIMEOUT__":
            await asyncio.sleep(0)
