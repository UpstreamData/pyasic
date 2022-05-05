from tools.cfg_util.cfg_util_qt.layout import (
    MINER_COUNT_BUTTONS,
    TABLE_KEYS,
    TABLE_HEADERS,
    window,
)
from tools.cfg_util.cfg_util_qt.imgs import TkImages, LIGHT
import PySimpleGUI as sg


def clear_tables():
    for table in TABLE_KEYS["table"]:
        window[table].update([])
    for tree in TABLE_KEYS["tree"]:
        window[tree].update(sg.TreeData())
    update_miner_count(0)


def update_miner_count(count):
    for button in MINER_COUNT_BUTTONS:
        window[button].update(f"Miners: {count}")


def update_tables(data: list):
    tables = {
        "SCAN": [["" for _ in TABLE_HEADERS["SCAN"]] for _ in data],
        "CMD": [["" for _ in TABLE_HEADERS["CMD"]] for _ in data],
        "POOLS": [["" for _ in TABLE_HEADERS["POOLS"]] for _ in data],
        "CONFIG": [["" for _ in TABLE_HEADERS["CONFIG"]] for _ in data],
    }
    for data_idx, item in enumerate(data):
        keys = item.keys()
        if "Hashrate" in keys:
            if not isinstance(item["Hashrate"], str):
                item[
                    "Hashrate"
                ] = f"{format(float(item['Hashrate']), '.2f').rjust(6, ' ')} TH/s"
        for key in keys:
            for table in TABLE_HEADERS.keys():
                for idx, header in enumerate(TABLE_HEADERS[table]):
                    if key == header:
                        tables[table][data_idx][idx] = item[key]

    window["scan_table"].update(tables["SCAN"])
    window["pools_table"].update(tables["POOLS"])
    window["cfg_table"].update(tables["CONFIG"])

    treedata = sg.TreeData()
    for idx, item in enumerate(tables["CMD"]):
        treedata.insert("", idx, "", item, icon=LIGHT)

    window["cmd_table"].update(treedata)

    update_miner_count(len(data))


async def _update_tree_by_ip(ip: str, data: dict):
    keys = data.keys()
    img = None
    if "IP" not in keys or "Model" not in keys:
        return
    _tree = window["cmd_table"].Widget
    for iid in _tree.get_children():
        values = _tree.item(iid)["values"]
        if data.get("Light"):
            if data["Light"]:
                img = TkImages().fault_light
            if not data["Light"]:
                img = TkImages().light
        if values[0] == ip:
            if img:
                _tree.item(
                    iid,
                    image=img,
                    values=[
                        data["IP"],
                        data["Model"] if "Model" in keys else "",
                        data["Command Output"] if "Command Output" in keys else "",
                    ],
                )
            else:
                _tree.item(
                    iid,
                    values=[
                        data["IP"],
                        data["Model"] if "Model" in keys else "",
                        data["Command Output"] if "Command Output" in keys else "",
                    ],
                )
