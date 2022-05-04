from tools.cfg_util.cfg_util_qt.tables import clear_tables, update_tables
from tools.cfg_util.cfg_util_qt.layout import window, update_prog_bar
from network import MinerNetwork
from miners.miner_factory import MinerFactory


async def scan_miners(network: MinerNetwork):
    clear_tables()
    scan_generator = network.scan_network_generator()
    MinerFactory().clear_cached_miners()

    progress_bar_len = 0
    network_size = len(network)
    await update_prog_bar(progress_bar_len, max=(2 * network_size))

    scanned_miners = []
    async for miner in scan_generator:
        if miner:
            scanned_miners.append(miner)
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)

    progress_bar_len += network_size - len(scanned_miners)
    await update_prog_bar(progress_bar_len)

    get_miner_genenerator = MinerFactory().get_miner_generator(scanned_miners)

    resolved_miners = []
    async for found_miner in get_miner_genenerator:
        resolved_miners.append(found_miner)
        resolved_miners.sort(key=lambda x: x.ip)
        update_tables([{"IP": str(miner.ip)} for miner in resolved_miners])
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)
