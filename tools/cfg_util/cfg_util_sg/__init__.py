from tools.cfg_util.cfg_util_sg.ui import ui

import asyncio
import sys

# Fix bug with some whatsminers and asyncio because of a socket not being shut down:
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ui())
