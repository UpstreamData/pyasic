import asyncio

from miners.miner_factory import MinerFactory
from tools.web_monitor._settings.func import get_current_settings


async def get_miner_data_dashboard(miner_ip):
    try:
        settings = get_current_settings()
        miner_identify_timeout = settings["miner_identify_timeout"]
        miner_data_timeout = settings["miner_data_timeout"]

        miner_ip = await asyncio.wait_for(
            MinerFactory().get_miner(miner_ip),
            miner_identify_timeout
        )

        miner_summary = await asyncio.wait_for(
            miner_ip.api.summary(),
            miner_data_timeout
        )
        if miner_summary:
            if 'MHS av' in miner_summary['SUMMARY'][0].keys():
                hashrate = format(
                    round(miner_summary['SUMMARY'][0]['MHS av'] / 1000000,
                          2), ".2f")
            elif 'GHS av' in miner_summary['SUMMARY'][0].keys():
                hashrate = format(
                    round(miner_summary['SUMMARY'][0]['GHS av'] / 1000, 2),
                    ".2f")
            else:
                hashrate = 0
        else:
            hashrate = 0

        return {"ip": str(miner_ip.ip), "hashrate": hashrate}

    except asyncio.exceptions.TimeoutError:
        return {"ip": miner_ip, "error": "The miner is not responding."}

    except KeyError:
        return {"ip": miner_ip,
                "error": "The miner returned unusable/unsupported data."}
