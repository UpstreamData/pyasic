import PySimpleGUI as sg
import asyncio
import sys
import base64
from io import BytesIO
from PIL import ImageTk, Image
from tools.cfg_util.cfg_util_qt.imgs import FAULT_LIGHT
from tools.cfg_util.cfg_util_qt.tables import clear_tables
from tools.cfg_util.cfg_util_qt.scan import btn_scan
from tools.cfg_util.cfg_util_qt.layout import window
import tkinter as tk

sg.set_options(font=("Liberation Mono", 10))


async def main():
    window.read(0)
    window["scan_table"].Widget.column(2, anchor=tk.W)

    while True:
        event, value = window.read(0)
        if event in (None, "Close", sg.WIN_CLOSED):
            sys.exit()
        if event == "btn_scan":
            await btn_scan(value["scan_ip"])
        if event == "__TIMEOUT__":
            await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
