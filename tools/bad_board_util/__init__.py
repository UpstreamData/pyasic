# TODO: Add Logging

# TODO: Add debug mode to settings?

# TODO: Add an option to append the last octet of the IP
#  address to the workername when configuring



from tools.bad_board_util.miner_factory import miner_factory
from tools.bad_board_util.ui import ui

import asyncio
import sys

# Fix bug with some whatsminers and asyncio because of a socket not being shut down:
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ui())


if __name__ == '__main__':
    main()
