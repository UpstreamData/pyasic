from cfg_util.miner_factory import miner_factory
from cfg_util.layout import window
from cfg_util.ui import ui

import asyncio


def main():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ui())
