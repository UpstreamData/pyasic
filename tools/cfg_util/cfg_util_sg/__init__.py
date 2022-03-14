# TODO: Add Logging

import asyncio
import sys
import logging

from tools.cfg_util.cfg_util_sg.ui import ui


# initialize logger and get settings
from logger import logger
logger.info("Initializing logger for CFG Util.")

# Fix bug with some whatsminers and asyncio because of a socket not being shut down:
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main():
    logging.info("Starting CFG Util.")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ui())
    logging.info("Closing CFG Util.")
