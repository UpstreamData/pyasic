from tools.cfg_util.layout import (
    MINER_COUNT_BUTTONS,
    TABLE_KEYS,
    TABLE_HEADERS,
    window,
)
from tools.cfg_util.imgs import TkImages, LIGHT, FAULT_LIGHT
import PySimpleGUI as sg
import ipaddress


def update_miner_count(count):
    for button in MINER_COUNT_BUTTONS:
        window[button].update(f"Miners: {count}")


def update_tables(data: list or None = None):
    TableManager().update_data(data)


def clear_tables():
    TableManager().clear_tables()


async def update_tree(data: list):
    for item in data:
        if not item.get("IP"):
            continue
        table_manager = TableManager()
        table_manager.update_tree_by_key(item, "IP")


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TableManager(metaclass=Singleton):
    _instance = None

    def __init__(self):
        self.images = TkImages()
        self.data = {}
        self.sort_key = "IP"
        self.sort_reverse = False

    def update_data(self, data: list):
        if not data:
            return

        for line in data:
            self.update_item(line)

    def update_sort_key(self, sort_key):
        if self.sort_key == sort_key:
            self.sort_reverse = not self.sort_reverse
        self.sort_key = sort_key
        self.update_tables()

    def update_item(self, data: dict):
        if not data or data == {} or not data.get("IP"):
            return

        if not data.get("Light"):
            data["Light"] = False

        if not data["IP"] in self.data.keys():
            self.data[data["IP"]] = {}

        for key in data.keys():
            self.data[data["IP"]][key] = data[key]

        self.update_tables()

    def update_tables(self):
        tables = {
            "SCAN": [["" for _ in TABLE_HEADERS["SCAN"]] for _ in self.data],
            "CMD": [["" for _ in TABLE_HEADERS["CMD"]] for _ in self.data],
            "POOLS_ALL": [["" for _ in TABLE_HEADERS["POOLS_ALL"]] for _ in self.data],
            "POOLS_1": [["" for _ in TABLE_HEADERS["POOLS_1"]] for _ in self.data],
            "POOLS_2": [["" for _ in TABLE_HEADERS["POOLS_2"]] for _ in self.data],
            "CONFIG": [["" for _ in TABLE_HEADERS["CONFIG"]] for _ in self.data],
        }

        ip_sorted_keys = sorted(self.data.keys(), key=lambda x: ipaddress.ip_address(x))
        sorted_keys = sorted(
            ip_sorted_keys, reverse=self.sort_reverse, key=lambda x: self._get_sort(x)
        )

        for data_idx, key in enumerate(sorted_keys):
            item = self.data[key]
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
        window["pools_table"].update(tables["POOLS_ALL"])
        window["pools_1_table"].update(tables["POOLS_1"])
        window["pools_2_table"].update(tables["POOLS_2"])
        window["cfg_table"].update(tables["CONFIG"])

        treedata = sg.TreeData()
        for idx, item in enumerate(tables["CMD"]):
            ico = LIGHT
            if self.data[item[0]]["Light"]:
                ico = FAULT_LIGHT
            treedata.insert("", idx, "", item, icon=ico)

        window["cmd_table"].update(treedata)

        update_miner_count(len(self.data))

    def _get_sort(self, data_key: str):
        if self.sort_key == "IP":
            return ipaddress.ip_address(self.data[data_key]["IP"])

        if self.sort_key == "Hashrate":
            if self.data[data_key]["Hashrate"] == "":
                return -1
            if not isinstance(self.data[data_key]["Hashrate"], str):
                return self.data[data_key]["Hashrate"]
            return float(
                self.data[data_key]["Hashrate"].replace(" ", "").replace("TH/s", "")
            )

        if self.sort_key in ["Wattage", "Temperature"]:
            if isinstance(self.data[data_key][self.sort_key], str):
                return -300

        if self.sort_key == "Split":
            if self.data[data_key][self.sort_key] == "":
                return -1
            if "/" not in self.data[data_key][self.sort_key]:
                return 0

            if not self.sort_reverse:
                return int(self.data[data_key][self.sort_key].split("/")[0])
            else:
                return int(self.data[data_key][self.sort_key].split("/")[1])

        return self.data[data_key][self.sort_key]

    def clear_tables(self):
        self.data = {}
        for table in TABLE_KEYS["table"]:
            window[table].update([])
        for tree in TABLE_KEYS["tree"]:
            window[tree].update(sg.TreeData())
        update_miner_count(0)
