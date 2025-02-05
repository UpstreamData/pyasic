"""Tests for hammer miners with firmware dating 2023-05-28 17-20-35 CST"""

import unittest
from dataclasses import fields
from unittest.mock import patch

from pyasic import APIError, MinerData
from pyasic.data import Fan, HashBoard
from pyasic.device.algorithm.hashrate.unit.scrypt import ScryptUnit
from pyasic.miners.elphapex import ElphapexDG1Plus

POOLS = [
    {
        "url": "stratum+tcp://stratum.pool.io:3333",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
    {
        "url": "stratum+tcp://stratum.pool.io:3334",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
    {
        "url": "stratum+tcp://stratum.pool.io:3335",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
]


data = {
    ElphapexDG1Plus: {
        "web_get_system_info": {
            "ipaddress": "172.19.203.183",
            "system_mode": "GNU/Linux",
            "netmask": "255.255.255.0",
            "gateway": "",
            "Algorithm": "Scrypt",
            "system_kernel_version": "4.4.194 #1 SMP Sat Sep 7 16:59:20 CST 2024",
            "system_filesystem_version": "DG1+_SW_V1.0.2",
            "nettype": "DHCP",
            "dnsservers": "",
            "netdevice": "eth0",
            "minertype": "DG1+",
            "macaddr": "12:34:56:78:90:12",
            "firmware_type": "Release",
            "hostname": "DG1+",
        },
        "web_summary": {
            "STATUS": {
                "STATUS": "S",
                "when": 2557706,
                "timestamp": 1731569527,
                "api_version": "1.0.0",
                "Msg": "summary",
            },
            "SUMMARY": [
                {
                    "rate_unit": "MH/s",
                    "elapsed": 357357,
                    "rate_30m": 0,
                    "rate_5s": 14920.940000000001,
                    "bestshare": 0,
                    "rate_ideal": 14229,
                    "status": [
                        {"status": "s", "type": "rate", "msg": "", "code": 0},
                        {"status": "s", "type": "network", "msg": "", "code": 0},
                        {"status": "s", "type": "fans", "msg": "", "code": 0},
                        {"status": "s", "type": "temp", "msg": "", "code": 0},
                    ],
                    "hw_all": 14199.040000000001,
                    "rate_avg": 14199.040000000001,
                    "rate_15m": 14415,
                }
            ],
            "INFO": {
                "miner_version": "DG1+_SW_V1.0.2",
                "CompileTime": "",
                "dev_sn": "28HY245192N000245C23B",
                "type": "DG1+",
                "hw_version": "DG1+_HW_V1.0",
            },
        },
        "web_stats": {
            "STATUS": {
                "STATUS": "S",
                "when": 2557700,
                "timestamp": 1731569521,
                "api_version": "1.0.0",
                "Msg": "stats",
            },
            "INFO": {
                "miner_version": "DG1+_SW_V1.0.2",
                "CompileTime": "",
                "dev_sn": "28HY245192N000245C23B",
                "type": "DG1+",
                "hw_version": "DG1+_HW_V1.0",
            },
            "STATS": [
                {
                    "rate_unit": "MH/s",
                    "elapsed": 357352,
                    "rate_30m": 0,
                    "rate_5s": 11531.879999999999,
                    "hwp_total": 0.11550000000000001,
                    "rate_ideal": 14229,
                    "chain": [
                        {
                            "freq_avg": 62000,
                            "index": 0,
                            "sn": "13HY245156N000581H11JB52",
                            "temp_chip": ["47125", "50500", "", ""],
                            "eeprom_loaded": True,
                            "rate_15m": 3507,
                            "hw": 204,
                            "temp_pcb": [47, 46, 67, 66],
                            "failrate": 0.029999999999999999,
                            "asic": "ooooooooo oooooooo oooooooo oooooooo oooo",
                            "rate_real": 3553.5,
                            "asic_num": 204,
                            "temp_pic": [47, 46, 67, 66],
                            "rate_ideal": 3557.25,
                            "hashrate": 3278.5999999999999,
                        },
                        {
                            "freq_avg": 62000,
                            "index": 1,
                            "sn": "13HY245156N000579H11JB52",
                            "temp_chip": ["52812", "56937", "", ""],
                            "eeprom_loaded": True,
                            "rate_15m": 3736,
                            "hw": 204,
                            "temp_pcb": [47, 46, 67, 66],
                            "failrate": 0.02,
                            "asic": "ooooooooo oooooooo oooooooo oooooooo oooo",
                            "rate_real": 3550.1100000000001,
                            "asic_num": 204,
                            "temp_pic": [47, 46, 67, 66],
                            "rate_ideal": 3557.25,
                            "hashrate": 3491.8400000000001,
                        },
                        {
                            "freq_avg": 62000,
                            "index": 2,
                            "sn": "13HY245156N000810H11JB52",
                            "temp_chip": ["48312", "51687", "", ""],
                            "eeprom_loaded": True,
                            "rate_15m": 3531,
                            "hw": 204,
                            "temp_pcb": [47, 46, 67, 66],
                            "failrate": 0.51000000000000001,
                            "asic": "ooooooooo oooooooo oooooooo oooooooo oooo",
                            "rate_real": 3551.8000000000002,
                            "asic_num": 204,
                            "temp_pic": [47, 46, 67, 66],
                            "rate_ideal": 3557.25,
                            "hashrate": 3408.6999999999998,
                        },
                        {
                            "freq_avg": 62000,
                            "index": 3,
                            "sn": "13HY245156N000587H11JB52",
                            "temp_chip": ["46500", "49062", "", ""],
                            "eeprom_loaded": True,
                            "rate_15m": 3641,
                            "hw": 204,
                            "temp_pcb": [47, 46, 67, 66],
                            "failrate": 0.029999999999999999,
                            "asic": "ooooooooo oooooooo oooooooo oooooooo oooo",
                            "rate_real": 3543.6300000000001,
                            "asic_num": 204,
                            "temp_pic": [47, 46, 67, 66],
                            "rate_ideal": 3557.25,
                            "hashrate": 3463.6799999999998,
                        },
                    ],
                    "rate_15m": 14415,
                    "chain_num": 4,
                    "fan": ["5340", "5400", "5400", "5400"],
                    "rate_avg": 14199.040000000001,
                    "fan_num": 4,
                }
            ],
        },
        "web_get_blink_status": {"blink": False},
        "web_get_miner_conf": {
            "pools": [
                {
                    "url": "stratum+tcp://ltc.trustpool.ru:3333",
                    "pass": "123",
                    "user": "Nikita9231.fworker",
                },
                {
                    "url": "stratum+tcp://ltc.trustpool.ru:443",
                    "pass": "123",
                    "user": "Nikita9231.fworker",
                },
                {
                    "url": "stratum+tcp://ltc.trustpool.ru:25",
                    "pass": "123",
                    "user": "Nikita9231.fworker",
                },
            ],
            "fc-voltage": "1470",
            "fc-fan-ctrl": False,
            "fc-freq-level": "100",
            "fc-fan-pwm": "80",
            "algo": "ltc",
            "fc-work-mode": 0,
            "fc-freq": "1850",
        },
        "web_pools": {
            "STATUS": {
                "STATUS": "S",
                "when": 5411762,
                "timestamp": 1738768594,
                "api_version": "1.0.0",
                "Msg": "pools",
            },
            "Device Total Rejected": 8888,
            "POOLS": [
                {
                    "diffs": 0,
                    "diffr": 524288,
                    "index": 0,
                    "user": "pool_username.real_worker",
                    "lsdiff": 524288,
                    "lstime": "00:00:18",
                    "diffa": 524288,
                    "accepted": 798704,
                    "diff1": 0,
                    "stale": 0,
                    "diff": "",
                    "rejected": 3320,
                    "status": "Unreachable",
                    "getworks": 802024,
                    "priority": 0,
                    "url": "stratum+tcp://stratum.pool.io:3333",
                },
                {
                    "diffs": 0,
                    "diffr": 524288,
                    "index": 1,
                    "user": "pool_username.real_worker",
                    "lsdiff": 524288,
                    "lstime": "00:00:00",
                    "diffa": 524288,
                    "accepted": 604803,
                    "diff1": 0,
                    "stale": 0,
                    "diff": "",
                    "rejected": 2492,
                    "status": "Alive",
                    "getworks": 607295,
                    "priority": 1,
                    "url": "stratum+tcp://stratum.pool.io:3334",
                },
                {
                    "diffs": 0,
                    "diffr": 524288,
                    "index": 2,
                    "user": "pool_username.real_worker",
                    "lsdiff": 524288,
                    "lstime": "00:00:05",
                    "diffa": 524288,
                    "accepted": 691522,
                    "diff1": 0,
                    "stale": 0,
                    "diff": "",
                    "rejected": 3076,
                    "status": "Unreachable",
                    "getworks": 694598,
                    "priority": 2,
                    "url": "stratum+tcp://stratum.pool.io:3335",
                },
            ],
            "Device Rejected%": 0.41999999999999998,
            "Device Total Work": 2103917,
            "INFO": {
                "miner_version": "DG1+_SW_V1.0.2",
                "CompileTime": "",
                "dev_sn": "28HY245192N000245C23B",
                "type": "DG1+",
                "hw_version": "DG1+_HW_V1.0",
            },
        },
    }
}


class TestElphapexMiners(unittest.IsolatedAsyncioTestCase):
    @patch("pyasic.rpc.base.BaseMinerRPCAPI._send_bytes")
    async def test_all_data_gathering(self, mock_send_bytes):
        mock_send_bytes.raises = APIError()
        for m_type in data:
            gathered_data = {}
            miner = m_type("127.0.0.1")
            for data_name in fields(miner.data_locations):
                if data_name.name == "config":
                    # skip
                    continue
                data_func = getattr(miner.data_locations, data_name.name)
                fn_args = data_func.kwargs
                args_to_send = {k.name: data[m_type][k.name] for k in fn_args}
                function = getattr(miner, data_func.cmd)
                gathered_data[data_name.name] = await function(**args_to_send)

            result = MinerData(
                ip=str(miner.ip),
                device_info=miner.device_info,
                expected_chips=(
                    miner.expected_chips * miner.expected_hashboards
                    if miner.expected_chips is not None
                    else 0
                ),
                expected_hashboards=miner.expected_hashboards,
                expected_fans=miner.expected_fans,
                hashboards=[
                    HashBoard(slot=i, expected_chips=miner.expected_chips)
                    for i in range(miner.expected_hashboards)
                ],
            )
            for item in gathered_data:
                if gathered_data[item] is not None:
                    setattr(result, item, gathered_data[item])

            self.assertEqual(result.mac, "12:34:56:78:90:12")
            self.assertEqual(result.api_ver, "1.0.0")
            self.assertEqual(result.fw_ver, "1.0.2")
            self.assertEqual(result.hostname, "DG1+")
            self.assertEqual(round(result.hashrate.into(ScryptUnit.MH)), 14199)
            self.assertEqual(
                result.fans,
                [Fan(speed=5340), Fan(speed=5400), Fan(speed=5400), Fan(speed=5400)],
            )
            self.assertEqual(result.total_chips, result.expected_chips)
            self.assertEqual(
                set([str(p.url) for p in result.pools]), set(p["url"] for p in POOLS)
            )
