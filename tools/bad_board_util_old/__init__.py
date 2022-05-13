from tools.bad_board_util_old.ui import ui

import asyncio
import sys
import logging

from logger import logger

logger.info("Initializing logger for Board Util.")


# Fix bug with some whatsminers and asyncio because of a socket not being shut down:
if (
    sys.version_info[0] == 3
    and sys.version_info[1] >= 8
    and sys.platform.startswith("win")
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main():
    logging.info("Starting Board Util.")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ui())
    logging.info("Closing Board Util.")


if __name__ == "__main__":
    main()
