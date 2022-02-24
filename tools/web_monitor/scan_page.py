from tools.web_monitor.app import sio
import json


async def scan_found_miner(miner):
    """Send data to client that a miner was scanned.

    :param miner: The miner object that was scanned.
    """
    await sio.emit('scan_found_miner', json.dumps(
        {
            "ip": str(miner.ip),
            "model": str(miner.model),
            "api": str(miner.api_type)
        }
    ))
