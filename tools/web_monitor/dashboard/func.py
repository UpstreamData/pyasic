import asyncio

from miners.miner_factory import MinerFactory
from tools.web_monitor._settings.func import (  # noqa - Ignore access to _module
    get_current_settings,
)


async def get_miner_data_dashboard(miner_ip):
    try:
        settings = get_current_settings()
        miner_identify_timeout = settings["miner_identify_timeout"]
        miner_data_timeout = settings["miner_data_timeout"]

        miner_ip = await asyncio.wait_for(
            MinerFactory().get_miner(miner_ip), miner_identify_timeout
        )

        data = await asyncio.wait_for(miner_ip.get_data(), miner_data_timeout)

        return {"ip": str(miner_ip.ip), "hashrate": data.hashrate}

    except asyncio.exceptions.TimeoutError:
        return {"ip": miner_ip, "error": "The miner is not responding."}

    except KeyError:
        return {
            "ip": miner_ip,
            "error": "The miner returned unusable/unsupported data.",
        }
