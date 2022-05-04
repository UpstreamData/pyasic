import PySimpleGUI as sg
import asyncio
import sys
import base64
from io import BytesIO
from PIL import ImageTk, Image
from tools.cfg_util.cfg_util_qt.imgs import FAULT_LIGHT
from tools.cfg_util.cfg_util_qt.tables import clear_tables
from tools.cfg_util.cfg_util_qt.scan import scan_miners
from network import MinerNetwork

from tools.cfg_util.cfg_util_qt.layout import window

sg.set_options(font=("Liberation Mono", 10))


async def main():
    window.read(0)
    # tree = window["command_table"]
    # tree_widget = tree.Widget
    # index = 0
    # iid = f"I{str(index + 1).rjust(3, '0')}"
    # img = ImageTk.PhotoImage(Image.open(BytesIO(base64.b64decode(FAULT_LIGHT))))
    # tree_widget.item(iid, image=img)
    # clear_tables()

    while True:
        event, value = window.read(0)
        if event in (None, "Close", sg.WIN_CLOSED):
            sys.exit()
        if event == "btn_scan":
            network = MinerNetwork("192.168.1.0")
            if value["scan_ip"]:
                ip, mask = value["scan_ip"].split("/")
                network = MinerNetwork(ip, mask=mask)
            asyncio.create_task(scan_miners(network))
        if event == "__TIMEOUT__":
            await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
