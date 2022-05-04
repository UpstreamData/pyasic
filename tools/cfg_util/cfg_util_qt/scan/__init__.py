import asyncio

from tools.cfg_util.cfg_util_qt.tables import clear_tables, update_tables
from tools.cfg_util.cfg_util_qt.layout import window, update_prog_bar
from network import MinerNetwork
from miners.miner_factory import MinerFactory
from API import APIError

import warnings
import logging

progress_bar_len = 0


async def scan_miners(network: MinerNetwork):
    clear_tables()
    scan_generator = network.scan_network_generator()
    MinerFactory().clear_cached_miners()

    global progress_bar_len

    network_size = len(network)
    await update_prog_bar(progress_bar_len, max=(3 * network_size))

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
    await update_prog_bar(network_size - len(resolved_miners))
    await get_miners_data(resolved_miners)


async def get_miners_data(miners: list):
    global progress_bar_len
    data_generator = asyncio.as_completed([_get_data(miner) for miner in miners])
    miner_data = [{"IP": str(miner.ip)} for miner in miners]
    for all_data in data_generator:
        data = await all_data
        for idx, item in enumerate(miner_data):
            # print(item["IP"], data["IP"])
            if item["IP"] == data["IP"]:
                miner_data[idx] = data
        update_tables(miner_data)
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)
    print("Done")


async def _get_data(miner):
    warnings.filterwarnings("ignore")
    miner_data = None
    host = await miner.get_hostname()
    try:
        model = await miner.get_model()
    except APIError:
        model = "?"
    if not model:
        model = "?"
    temps = 0
    th5s = 0
    wattage = 0
    user = "?"

    try:
        miner_data = await miner.api.multicommand(
            "summary", "devs", "temps", "tunerstatus", "pools", "stats"
        )
    except APIError:
        try:
            # no devs command, it will fail in this case
            miner_data = await miner.api.multicommand(
                "summary", "temps", "tunerstatus", "pools", "stats"
            )
        except APIError as e:
            logging.warning(f"{str(miner.ip)}: {e}")
            return {
                "IP": str(miner.ip),
                "Model": "Unknown",
                "Hostname": "Unknown",
                "Hashrate": 0,
                "Temperature": 0,
                "Pool User": "Unknown",
                "Wattage": 0,
                "Split": 0,
                "Pool 1": "Unknown",
                "Pool 1 User": "Unknown",
                "Pool 2": "Unknown",
                "Pool 2 User": "Unknown",
            }
    if miner_data:
        logging.info(f"Received miner data for miner: {miner.ip}")
        # get all data from summary
        if "summary" in miner_data.keys():
            if (
                not miner_data["summary"][0].get("SUMMARY") == []
                and "SUMMARY" in miner_data["summary"][0].keys()
            ):
                # temperature data, this is the idea spot to get this
                if "Temperature" in miner_data["summary"][0]["SUMMARY"][0].keys():
                    if (
                        not round(miner_data["summary"][0]["SUMMARY"][0]["Temperature"])
                        == 0
                    ):
                        temps = miner_data["summary"][0]["SUMMARY"][0]["Temperature"]
                # hashrate data
                if "MHS av" in miner_data["summary"][0]["SUMMARY"][0].keys():
                    th5s = format(
                        round(
                            miner_data["summary"][0]["SUMMARY"][0]["MHS av"] / 1000000,
                            2,
                        ),
                        ".2f",
                    ).rjust(6, " ")
                elif "GHS av" in miner_data["summary"][0]["SUMMARY"][0].keys():
                    if not miner_data["summary"][0]["SUMMARY"][0]["GHS av"] == "":
                        th5s = format(
                            round(
                                float(miner_data["summary"][0]["SUMMARY"][0]["GHS av"])
                                / 1000,
                                2,
                            ),
                            ".2f",
                        ).rjust(6, " ")

        # alternate temperature data, for BraiinsOS
        if "temps" in miner_data.keys():
            if not miner_data["temps"][0].get("TEMPS") == []:
                if "Chip" in miner_data["temps"][0]["TEMPS"][0].keys():
                    for board in miner_data["temps"][0]["TEMPS"]:
                        if board["Chip"] is not None and not board["Chip"] == 0.0:
                            temps = board["Chip"]
        # alternate temperature data, for Whatsminers
        if "devs" in miner_data.keys():
            if not miner_data["devs"][0].get("DEVS") == []:
                if "Chip Temp Avg" in miner_data["devs"][0]["DEVS"][0].keys():
                    for board in miner_data["devs"][0]["DEVS"]:
                        if (
                            board["Chip Temp Avg"] is not None
                            and not board["Chip Temp Avg"] == 0.0
                        ):
                            temps = board["Chip Temp Avg"]
        # alternate temperature data
        if "stats" in miner_data.keys():
            if not miner_data["stats"][0]["STATS"] == []:
                for temp in ["temp2", "temp1", "temp3"]:
                    if temp in miner_data["stats"][0]["STATS"][1].keys():
                        if (
                            miner_data["stats"][0]["STATS"][1][temp] is not None
                            and not miner_data["stats"][0]["STATS"][1][temp] == 0.0
                        ):
                            temps = miner_data["stats"][0]["STATS"][1][temp]
            # alternate temperature data, for Avalonminers
            miner_data["stats"][0]["STATS"][0].keys()
            if any(
                "MM ID" in string
                for string in miner_data["stats"][0]["STATS"][0].keys()
            ):
                temp_all = []
                for key in [
                    string
                    for string in miner_data["stats"][0]["STATS"][0].keys()
                    if "MM ID" in string
                ]:
                    for value in [
                        string
                        for string in miner_data["stats"][0]["STATS"][0][key].split(" ")
                        if "TMax" in string
                    ]:
                        temp_all.append(int(value.split("[")[1].replace("]", "")))
                temps = round(sum(temp_all) / len(temp_all))

        # pool information
        if "pools" in miner_data.keys():
            if not miner_data["pools"][0].get("POOLS") == []:
                user = miner_data["pools"][0]["POOLS"][0]["User"]

            else:
                print(miner_data["pools"][0])
                user = "Blank"

        # braiins tuner status / wattage
        if "tunerstatus" in miner_data.keys():
            wattage = miner_data["tunerstatus"][0]["TUNERSTATUS"][0]["PowerLimit"]

        elif "Power" in miner_data["summary"][0]["SUMMARY"][0].keys():
            wattage = miner_data["summary"][0]["SUMMARY"][0]["Power"]

    ret_data = {
        "Hashrate": th5s,
        "IP": str(miner.ip),
        "Model": model,
        "Temperature": round(temps),
        "Hostname": host,
        "Pool User": user,
        "Pool 1 User": user,
        "Wattage": wattage,
    }

    logging.debug(f"{ret_data}")

    return ret_data
