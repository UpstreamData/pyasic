from tools.cfg_util.cfg_util_qt.layout import TABLE_KEYS, TABLE_HEADERS, window
from tools.cfg_util.cfg_util_qt.imgs import LIGHT
from PySimpleGUI import TreeData


def clear_tables():
    for table in TABLE_KEYS["table"]:
        window[table].update([])
    for tree in TABLE_KEYS["tree"]:
        window[tree].update(TreeData())


def update_tables(data: dict):
    tables = {
        "SCAN": [["" for _ in TABLE_HEADERS["SCAN"]] for _ in data],
        "CMD": [["" for _ in TABLE_HEADERS["CMD"]] for _ in data],
        "POOLS": [["" for _ in TABLE_HEADERS["POOLS"]] for _ in data],
        "CONFIG": [["" for _ in TABLE_HEADERS["CONFIG"]] for _ in data],
    }
    for data_idx, item in enumerate(data):
        for key in item.keys():
            for table in TABLE_HEADERS.keys():
                for idx, header in enumerate(TABLE_HEADERS[table]):
                    if key == header:
                        tables[table][data_idx][idx] = item[key]

    window["scan_table"].update(tables["SCAN"])
    window["pools_table"].update(tables["POOLS"])
    window["cfg_table"].update(tables["CONFIG"])

    tree_data = TreeData()
    for item in tables["CMD"]:
        tree_data.insert("", "", "", item, icon=LIGHT)

    window["cmd_table"].update(tree_data)
