import asyncio

from miners.miner_factory import MinerFactory
from network import MinerNetwork
from tools.cfg_util.decorators import disable_buttons
from tools.cfg_util.layout import window, update_prog_bar, TABLE_HEADERS
from tools.cfg_util.tables import clear_tables, TableManager

progress_bar_len = 0


DEFAULT_DATA = set()

for table in TABLE_HEADERS:
    for header in TABLE_HEADERS[table]:
        DEFAULT_DATA.add(header)


async def btn_all():
    table = "scan_table"
    window[table].update(
        select_rows=([row for row in range(len(window[table].Values))])
    )


async def btn_scan(scan_ip: str):
    network = MinerNetwork("192.168.1.0")
    if scan_ip:
        if "/" in scan_ip:
            ip, mask = scan_ip.split("/")
            network = MinerNetwork(ip, mask=mask)
        else:
            network = MinerNetwork(scan_ip)
    asyncio.create_task(_scan_miners(network))


@disable_buttons("Scanning")
async def _scan_miners(network: MinerNetwork):
    """Scan the given network for miners, get data, and fill in the table."""
    # clear the tables on the config tool to prepare for new miners
    clear_tables()

    # clear miner factory cache to make sure we are getting correct miners
    MinerFactory().clear_cached_miners()

    # create async generator to scan network for miners
    scan_generator = network.scan_network_generator()

    # set progress bar length to 2x network size and reset it to 0
    global progress_bar_len
    progress_bar_len = 0
    network_size = len(network)
    await update_prog_bar(progress_bar_len, _max=(2 * network_size))

    #  asynchronously get each miner scanned by the generator
    miners = []
    async for miner in scan_generator:
        # if the generator yields a miner, add it to our list
        if miner:
            miners.append(miner)

            # sort the list of miners by IP
            miners.sort()

            _data = {}
            for key in DEFAULT_DATA:
                _data[key] = ""
            _data["IP"] = str(miner.ip)
            TableManager().update_item(_data)

            asyncio.create_task(_get_miner_data(miner))

        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)

    progress_bar_len += network_size - len(miners)
    await update_prog_bar(progress_bar_len)


async def _get_miner_data(miner):
    global progress_bar_len

    TableManager().update_item(await _get_data(miner))

    progress_bar_len += 1
    await update_prog_bar(progress_bar_len)


async def _get_data(miner):
    return await miner.get_data()
