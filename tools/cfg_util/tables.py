from tools.cfg_util.layout import (
    MINER_COUNT_BUTTONS,
    HASHRATE_TOTAL_BUTTONS,
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


def update_total_hr(hashrate: float):
    if hashrate > 999:
        hashrate = f"{round(hashrate/1000, 2)} PH/s"
    else:
        hashrate = f"{round(hashrate)} TH/s"
    for button in HASHRATE_TOTAL_BUTTONS:
        window[button].update(f"Hashrate: {hashrate}")


def update_tables(data: list or None = None):
    TableManager().update_data(data)


def clear_tables():
    TableManager().clear_tables()


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
        if "▲" in sort_key or "▼" in sort_key:
            sort_key = sort_key[:-1]
        if self.sort_key == sort_key:
            self.sort_reverse = not self.sort_reverse
        self.sort_key = sort_key
        self.update_tables()

    def update_item(self, data: dict):
        if not data or data == {} or not data.get("IP"):
            return

        if not data["IP"] in self.data.keys():
            self.data[data["IP"]] = {}

        if not data.get("Light") and not self.data[data["IP"]].get("Light"):
            data["Light"] = False

        for key in data.keys():
            self.data[data["IP"]][key] = data[key]

        self.update_tables()

    def update_tables(self):
        tables = {
            "SCAN": [["" for _ in TABLE_HEADERS["SCAN"]] for _ in self.data],
            "CMD": [["" for _ in TABLE_HEADERS["CMD"]] for _ in self.data],
            "BOARDS": [["" for _ in TABLE_HEADERS["BOARDS"]] for _ in self.data],
            "POOLS_ALL": [["" for _ in TABLE_HEADERS["POOLS_ALL"]] for _ in self.data],
            "POOLS_1": [["" for _ in TABLE_HEADERS["POOLS_1"]] for _ in self.data],
            "POOLS_2": [["" for _ in TABLE_HEADERS["POOLS_2"]] for _ in self.data],
            "CONFIG": [["" for _ in TABLE_HEADERS["CONFIG"]] for _ in self.data],
        }

        ip_sorted_keys = sorted(self.data.keys(), key=lambda x: ipaddress.ip_address(x))
        sorted_keys = sorted(
            ip_sorted_keys, reverse=self.sort_reverse, key=lambda x: self._get_sort(x)
        )

        table_names = {
            "SCAN": "scan_table",
            "BOARDS": "boards_table",
            "POOLS_ALL": "pools_table",
            "POOLS_1": "pools_1_table",
            "POOLS_2": "pools_2_table",
            "CONFIG": "cfg_table",
            "CMD": "cmd_table",
        }

        for table in TABLE_HEADERS.keys():
            widget = window[table_names[table]].Widget
            for idx, header in enumerate(TABLE_HEADERS[table]):
                _header = header
                if header == self.sort_key:
                    if self.sort_reverse:
                        _header = f"{header}▼"
                    else:
                        _header = f"{header}▲"
                widget.heading(idx, text=_header)

        # reset light
        window["cmd_table"].Widget.heading("#0", text="Light")

        # handle light sort key
        if self.sort_key == "Light":
            widget = window["cmd_table"].Widget
            idx = "#0"
            if self.sort_reverse:
                _header = f"Light▼"
            else:
                _header = f"Light▲"
            widget.heading(idx, text=_header)

        for data_idx, key in enumerate(sorted_keys):
            item = self.data[key]
            keys = item.keys()

            if "Hashrate" in keys:
                if not isinstance(item["Hashrate"], str):
                    item[
                        "Hashrate"
                    ] = f"{format(float(item['Hashrate']), '.2f').rjust(6, ' ')} TH/s"

            if "Chip %" in keys:
                if not isinstance(item["Chip %"], str):
                    item["Chip %"] = f"{item['Chip %']}%"

            for _key in keys:
                for table in TABLE_HEADERS.keys():
                    for idx, header in enumerate(TABLE_HEADERS[table]):
                        if _key == header:
                            tables[table][data_idx][idx] = item[_key]

        window["scan_table"].update(tables["SCAN"])
        window["boards_table"].update(tables["BOARDS"])
        window["pools_table"].update(tables["POOLS_ALL"])
        window["pools_1_table"].update(tables["POOLS_1"])
        window["pools_2_table"].update(tables["POOLS_2"])
        window["cfg_table"].update(tables["CONFIG"])

        treedata = sg.TreeData()
        for idx, item in enumerate(tables["CMD"]):
            ico = LIGHT
            status = " Off"
            if self.data[item[0]]["Light"]:
                ico = FAULT_LIGHT
                status = " On"
            treedata.insert("", idx, status, item, icon=ico)

        window["cmd_table"].update(treedata)

        update_miner_count(len(self.data))
        total_hr = 0
        for key in self.data.keys():
            hashrate = 0
            if not self.data[key]["Hashrate"] == "":
                hashrate = (
                    self.data[key]["Hashrate"].replace(" ", "").replace("TH/s", "")
                )
            total_hr += float(hashrate)
        update_total_hr(round(total_hr))

    def _get_sort(self, data_key: str):
        if self.sort_key not in self.data[data_key]:
            print(self.data[data_key])
            return ""

        if self.sort_key == "IP":
            return ipaddress.ip_address(self.data[data_key]["IP"])

        if self.sort_key == "Chip %":
            return int((self.data[data_key]["Chip %"]).replace("%", ""))

        if self.sort_key == "Hashrate":
            if self.data[data_key]["Hashrate"] == "":
                return -1
            if not isinstance(self.data[data_key]["Hashrate"], str):
                return self.data[data_key]["Hashrate"]
            return float(
                self.data[data_key]["Hashrate"].replace(" ", "").replace("TH/s", "")
            )

        if self.sort_key in [
            "Wattage",
            "Temp",
            "Total",
            "Ideal",
            "Left Chips",
            "Center Chips",
            "Right Chips",
        ]:
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
