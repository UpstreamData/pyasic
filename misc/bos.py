import asyncio
from network import MinerNetwork
from miners.bosminer import BOSMiner


async def get_bos_bad_tuners():
    miner_network = MinerNetwork("192.168.1.0")
    miners = await miner_network.scan_network_for_miners()
    tuner_tasks = []
    for miner in miners:
        # can only do this if its a subclass of BOSMiner
        if BOSMiner in type(miner).__bases__:
            tuner_tasks.append(_get_tuner_status(miner))
    tuner_status = await asyncio.gather(*tuner_tasks)
    bad_tuner_miners = []
    for item in tuner_status:
        bad_boards = []
        for board in item["tuner_status"]:
            if board["status"] not in ["Stable", "Testing performance profile"]:
                bad_boards.append({"board": board["board"],
                                   "error": board["status"].replace("Hashchain refused to start: ", "")})
        if len(bad_boards) > 0:
            bad_tuner_miners.append({"ip": item["ip"], "boards": bad_boards})
    return bad_tuner_miners


async def _get_tuner_status(miner):
    tuner_status = await miner.api.tunerstatus()
    tuner_data = []
    if tuner_status:
        for board in tuner_status["TUNERSTATUS"][0]["TunerChainStatus"]:
            tuner_data.append({"board": board["HashchainIndex"], "status": board["Status"]})
    return {"ip": str(miner.ip), "tuner_status": tuner_data}
