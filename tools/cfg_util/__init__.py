import asyncio
import sys

from .ui import ui

# Fix bug with some whatsminers and asyncio because of a socket not being shut down:
if (
    sys.version_info[0] == 3
    and sys.version_info[1] >= 8
    and sys.platform.startswith("win")
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main():
    asyncio.run(ui())


if __name__ == "__main__":
    main()
