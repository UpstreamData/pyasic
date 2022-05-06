import PySimpleGUI as sg
import asyncio
import sys
from tools.cfg_util.cfg_util_qt.imgs import FAULT_LIGHT, TkImages
from tools.cfg_util.cfg_util_qt.scan import btn_scan
from tools.cfg_util.cfg_util_qt.commands import btn_light
from tools.cfg_util.cfg_util_qt.layout import window
from tools.cfg_util.cfg_util_qt.general import btn_all, btn_web, btn_refresh
from tools.cfg_util.cfg_util_qt.tables import TableManager
import tkinter as tk

sg.set_options(font=("Liberation Mono", 10))


async def main():
    window.read(0)

    # create images used in the table, they will not show if not saved here
    tk_imgs = TkImages()

    # left justify hostnames
    window["scan_table"].Widget.column(2, anchor=tk.W)

    # cmd table sort event
    window["cmd_table"].Widget.bind("<Button-1>", lambda x: print("clicked"))

    while True:
        event, value = window.read(0)
        if event in (None, "Close", sg.WIN_CLOSED):
            sys.exit()

        if isinstance(event, tuple):
            if len(window["scan_table"].Values) > 0:
                if event[0].endswith("_table"):
                    if event[2][0] == -1:
                        mgr = TableManager()
                        table = window[event[0]].Widget
                        mgr.update_sort_key(table.heading(event[2][1])["text"])

        # scan tab

        if event == "scan_all":
            _table = "scan_table"
            btn_all(_table, value[_table])
        if event == "scan_web":
            _table = "scan_table"
            btn_web(_table, value[_table])
        if event == "scan_refresh":
            _table = "scan_table"
            asyncio.create_task(btn_refresh(_table, value[_table]))
        if event == "btn_scan":
            await btn_scan(value["scan_ip"])

        # pools tab
        if event == "pools_all":
            _table = "pools_table"
            btn_all(_table, value[_table])
        if event == "pools_web":
            _table = "pools_table"
            btn_web(_table, value[_table])
        if event == "pools_refresh":
            _table = "pools_table"
            asyncio.create_task(btn_refresh(_table, value[_table]))

        # configure tab
        if event == "cfg_all":
            _table = "cfg_table"
            btn_all(_table, value[_table])
        if event == "cfg_web":
            _table = "cfg_table"
            btn_web(_table, value[_table])

        # commands tab
        if event == "cmd_all":
            _table = "cmd_table"
            btn_all(_table, value[_table])

        if event == "cmd_light":
            _table = "cmd_table"
            _ips = value[_table]
            await btn_light(_ips)

        if event == "__TIMEOUT__":
            await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
