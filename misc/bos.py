import asyncio
from network import MinerNetwork
from miners.bosminer import BOSMiner


async def get_bos_bad_tuners(ip: str = "192.168.1.0", mask: int = 24):
    # create a miner network
    miner_network = MinerNetwork(ip, mask=mask)

    # scan for miners
    miners = await miner_network.scan_network_for_miners()

    # create an empty list of tasks
    tuner_tasks = []

    # loop checks if the miner is a BOSMiner
    for miner in miners:
        # can only do this if its a subclass of BOSMiner
        if BOSMiner in type(miner).__bases__:
            tuner_tasks.append(_get_tuner_status(miner))

    # run all the tuner status commands
    tuner_status = await asyncio.gather(*tuner_tasks)

    # create a list of all miners with bad board tuner status
    bad_tuner_miners = []
    for item in tuner_status:
        # loop through and get each miners' bad board count
        bad_boards = []
        for board in item["tuner_status"]:
            # if its not stable or still testing, its bad
            if board["status"] not in ["Stable", "Testing performance profile", "Tuning individual chips"]:
                # remove the part about the board refusing to start
                bad_boards.append({"board": board["board"],
                                   "error": board["status"].replace("Hashchain refused to start: ", "")})

        # if this miner has bad boards, add it to the list of bad board miners
        if len(bad_boards) > 0:
            bad_tuner_miners.append({"ip": item["ip"], "boards": bad_boards})

    # return the list of bad board miners
    return bad_tuner_miners


async def _get_tuner_status(miner):
    # run the tunerstatus command, since the miner will always be BOSMiner
    tuner_status = await miner.api.tunerstatus()

    # create a list to add the tuner data to
    tuner_data = []

    # if we have data, loop through to get the hashchain status
    if tuner_status:
        for board in tuner_status["TUNERSTATUS"][0]["TunerChainStatus"]:
            tuner_data.append({"board": board["HashchainIndex"], "status": board["Status"]})

    # return the data along with the IP or later tracking
    return {"ip": str(miner.ip), "tuner_status": tuner_data}
