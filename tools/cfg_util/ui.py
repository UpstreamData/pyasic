import PySimpleGUI as sg
import asyncio
import sys
from tools.cfg_util.imgs import TkImages
from tools.cfg_util.scan import btn_scan
from tools.cfg_util.commands import (
    btn_light,
    btn_reboot,
    btn_backend,
    btn_command,
)
from tools.cfg_util.configure import (
    generate_config_ui,
    btn_import,
    btn_config,
)
from tools.cfg_util.layout import window, TABLE_KEYS
from tools.cfg_util.general import btn_all, btn_web, btn_refresh
from tools.cfg_util.tables import TableManager
import tkinter as tk
import pyperclip


def _tree_header_click_handler(event, table):
    region = table.Widget.identify("region", event.x, event.y)
    if region == "heading":
        col = int(table.Widget.identify_column(event.x)[1:]) - 1

        if col == -1:
            # handle the "Light" column, which needs a key of #0
            col = "#0"

        heading = table.Widget.heading(col)["text"]

        mgr = TableManager()
        mgr.update_sort_key(heading)


def _table_copy(table):
    selection = window[table].Widget.selection()
    _copy_values = []
    for each in selection:
        try:
            value = window[table].Widget.item(each)["values"]
            values = []
            for item in value:
                values.append(str(item).strip())
            _copy_values.append(values)
        except Exception as E:
            pass

    copy_values = []
    for item in _copy_values:
        copy_values.append(", ".join(item))
    copy_string = "\n".join(copy_values)
    pyperclip.copy(copy_string)


def _table_select_all(table):
    if table in TABLE_KEYS["table"]:
        window[table].update(
            select_rows=([row for row in range(len(window[table].Values))])
        )

    if table in TABLE_KEYS["tree"]:
        _tree = window[table]
        rows_to_select = [i for i in _tree.Widget.get_children()]
        _tree.Widget.selection_set(rows_to_select)


def bind_copy(key):
    widget = window[key].Widget
    widget.bind("<Control-Key-c>", lambda x: _table_copy(key))


def bind_ctrl_a(key):
    widget = window[key].Widget
    widget.bind("<Control-Key-a>", lambda x: _table_select_all(key))


async def ui():
    window.read(0)
    TableManager().update_tables()

    for key in [*TABLE_KEYS["table"], *TABLE_KEYS["tree"]]:
        bind_copy(key)
        bind_ctrl_a(key)

    # create images used in the table, they will not show if not saved here
    tk_imgs = TkImages()

    # left justify hostnames
    window["scan_table"].Widget.column(2, anchor=tk.W)

    # cmd table sort event
    window["cmd_table"].Widget.bind(
        "<Button-1>", lambda x: _tree_header_click_handler(x, window["cmd_table"])
    )

    while True:
        event, value = window.read(0)
        if event in (None, "Close", sg.WIN_CLOSED):
            sys.exit()

        if isinstance(event, tuple):
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
            asyncio.create_task(btn_scan(value["scan_ip"]))

        # boards tab
        if event == "boards_all":
            _table = "boards_table"
            btn_all(_table, value[_table])
        if event == "boards_web":
            _table = "boards_table"
            btn_web(_table, value[_table])
        if event == "boards_refresh":
            _table = "boards_table"
            asyncio.create_task(btn_refresh(_table, value[_table]))

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
        if event == "cfg_generate":
            await generate_config_ui()
        if event == "cfg_import":
            _table = "cfg_table"
            asyncio.create_task(btn_import(_table, value[_table]))
        if event == "cfg_config":
            _table = "cfg_table"
            asyncio.create_task(
                btn_config(
                    _table,
                    value[_table],
                    value["cfg_config_txt"],
                    value["cfg_append_ip"],
                )
            )

        # commands tab
        if event == "cmd_all":
            _table = "cmd_table"
            btn_all(_table, value[_table])
        if event == "cmd_light":
            _table = "cmd_table"
            _ips = value[_table]
            asyncio.create_task(btn_light(_ips))
        if event == "cmd_reboot":
            _table = "cmd_table"
            _ips = value[_table]
            asyncio.create_task(btn_reboot(_ips))
        if event == "cmd_backend":
            _table = "cmd_table"
            _ips = value[_table]
            asyncio.create_task(btn_backend(_ips))
        if event == "btn_cmd":
            _table = "cmd_table"
            _ips = value[_table]
            asyncio.create_task(btn_command(_ips, value["cmd_txt"]))

        if event == "__TIMEOUT__":
            await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(ui())
