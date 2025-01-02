"""Tests for hammer miners with firmware dating 2023-05-28 17-20-35 CST"""

import unittest
from dataclasses import fields
from unittest.mock import patch

from pyasic import APIError, MinerData
from pyasic.data import Fan, HashBoard
from pyasic.device.algorithm.hashrate.unit.scrypt import ScryptUnit
from pyasic.miners.hammer import HammerD10

POOLS = [
    {
        "url": "stratum+tcp://stratum.pool.io:3333",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
    {
        "url": "stratum+tcp://stratum.pool.io:3333",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
    {
        "url": "stratum+tcp://stratum.pool.io:3333",
        "user": "pool_username.real_worker",
        "pwd": "123",
    },
]

data = {
    HammerD10: {
        "web_get_system_info": {
            "minertype": "Hammer D10",
            "nettype": "DHCP",
            "netdevice": "eth0",
            "macaddr": "12:34:56:78:90:12",
            "hostname": "Hammer",
            "ipaddress": "10.0.0.1",
            "netmask": "255.255.255.0",
            "gateway": "",
            "dnsservers": "",
            "curtime": "18:46:15",
            "uptime": "92",
            "loadaverage": "1.06, 1.36, 1.48",
            "mem_total": "251180",
            "mem_used": "64392",
            "mem_free": "186788",
            "mem_buffers": "0",
            "mem_cached": "0",
            "system_mode": "GNU/Linux",
            "bb_hwv": "2.0.2.2",
            "system_kernel_version": "Linux 3.8.13 #22 SMP Tue Dec 2 15:26:11 CST 2014",
            "system_filesystem_version": "2022-11-11 13-46-30 CST",
            "cgminer_version": "2.3.3",
        },
        "rpc_version": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 1730228015,
                    "Code": 22,
                    "Msg": "CGMiner versions",
                    "Description": "ccminer 2.3.3",
                }
            ],
            "VERSION": [
                {
                    "CGMiner": "2.3.3",
                    "API": "3.1",
                    "Miner": "2.0.2.2",
                    "CompileTime": "2023-05-28 17-20-35 CST",
                    "Type": "Hammer D10",
                }
            ],
            "id": 1,
        },
        "rpc_stats": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 1730228065,
                    "Code": 70,
                    "Msg": "CGMiner stats",
                    "Description": "ccminer 2.3.3",
                }
            ],
            "STATS": [
                {
                    "CGMiner": "2.3.3",
                    "Miner": "2.0.2.2",
                    "CompileTime": "2023-05-28 17-20-35 CST",
                    "Type": "Hammer D10",
                },
                {
                    "STATS": 0,
                    "ID": "A30",
                    "Elapsed": 119161,
                    "Calls": 0,
                    "Wait": 0.000000,
                    "Max": 0.000000,
                    "Min": 99999999.000000,
                    "MHS 5s": "4686.4886",
                    "MHS av": "4872.8713",
                    "miner_count": 3,
                    "frequency": "810",
                    "fan_num": 4,
                    "fan1": 4650,
                    "fan2": 4500,
                    "fan3": 3870,
                    "fan4": 3930,
                    "temp_num": 12,
                    "temp1": 21,
                    "temp1": 42,
                    "temp1": 21,
                    "temp1": 45,
                    "temp2": 21,
                    "temp2": 40,
                    "temp2": 23,
                    "temp2": 42,
                    "temp3": 18,
                    "temp3": 39,
                    "temp3": 20,
                    "temp3": 40,
                    "temp4": 0,
                    "temp4": 0,
                    "temp4": 0,
                    "temp4": 0,
                    "temp_max": 52,
                    "Device Hardware%": 0.0000,
                    "no_matching_work": 7978,
                    "chain_acn1": 108,
                    "chain_acn2": 108,
                    "chain_acn3": 108,
                    "chain_acn4": 0,
                    "chain_acs1": " oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooo",
                    "chain_acs2": " oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooo",
                    "chain_acs3": " oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooooooo oooo",
                    "chain_acs4": "",
                    "chain_hw1": 2133,
                    "chain_hw2": 2942,
                    "chain_hw3": 2903,
                    "chain_hw4": 0,
                    "chain_rate1": "1578.2742",
                    "chain_rate2": "1594.3646",
                    "chain_rate3": "1513.8498",
                    "chain_rate4": "",
                },
            ],
            "id": 1,
        },
        "rpc_summary": {
            "STATUS": [
                {
                    "STATUS": "S",
                    "When": 1730228038,
                    "Code": 11,
                    "Msg": "Summary",
                    "Description": "ccminer 2.3.3",
                }
            ],
            "SUMMARY": [
                {
                    "Elapsed": 119134,
                    "MHS 5s": "4885.0813",
                    "MHS av": "4872.9297",
                    "Found Blocks": 0,
                    "Getworks": 8842,
                    "Accepted": "156.0000",
                    "Rejected": "156.0000",
                    "Hardware Errors": 7977,
                    "Utility": 6.71,
                    "Discarded": 76514,
                    "Stale": 0,
                    "Get Failures": 0,
                    "Local Work": 4123007,
                    "Remote Failures": 0,
                    "Network Blocks": 3323,
                    "Total MH": 580531131.4496,
                    "Work Utility": 4485762.79,
                    "Difficulty Accepted": 8804959701.00000000,
                    "Difficulty Rejected": 101813978.00000000,
                    "Difficulty Stale": 0.00000000,
                    "Best Share": 80831,
                    "Device Hardware%": 0.0001,
                    "Device Rejected%": 1.1431,
                    "Pool Rejected%": 1.1431,
                    "Pool Stale%": 0.0000,
                    "Last getwork": 1730228038,
                }
            ],
            "id": 1,
        },
        "web_summary": {
            "STATUS": {
                "STATUS": "S",
                "when": 1732121812.35528,
                "Msg": "summary",
                "api_version": "1.0.0",
            },
            "INFO": {
                "miner_version": "49.0.1.3",
                "CompileTime": "Fri Sep 15 14:39:20 CST 2023",
                "type": "Antminer S19j",
            },
            "SUMMARY": [
                {
                    "elapsed": 10023,
                    "rate_5s": 102000.0,
                    "rate_30m": 102000.0,
                    "rate_avg": 102000.0,
                    "rate_ideal": 102000.0,
                    "rate_unit": "GH/s",
                    "hw_all": 1598,
                    "bestshare": 10000000000,
                    "status": [
                        {"type": "rate", "status": "s", "code": 0, "msg": ""},
                        {"type": "network", "status": "s", "code": 0, "msg": ""},
                        {"type": "fans", "status": "s", "code": 0, "msg": ""},
                        {"type": "temp", "status": "s", "code": 0, "msg": ""},
                    ],
                }
            ],
        },
        "web_get_blink_status": {"code": "B000"},
        "web_get_conf": {
            "pools": [
                {
                    "url": p["url"],
                    "user": p["user"],
                    "pass": p["pwd"],
                }
                for p in POOLS
            ],
            "api-listen": True,
            "api-network": True,
            "api-groups": "A:stats:pools:devs:summary:version",
            "api-allow": "A:0/0,W:*",
            "bitmain-fan-ctrl": False,
            "bitmain-fan-pwm": "100",
            "bitmain-use-vil": True,
            "bitmain-freq": "675",
            "bitmain-voltage": "1400",
            "bitmain-ccdelay": "0",
            "bitmain-pwth": "0",
            "bitmain-work-mode": "0",
            "bitmain-freq-level": "",
        },
        "rpc_pools": {
            "STATUS": [
                {
                    "Code": 7,
                    "Description": "cgminer 1.0.0",
                    "Msg": "3 Pool(s)",
                    "STATUS": "S",
                    "When": 1732121693,
                }
            ],
            "POOLS": [
                {
                    "Accepted": 10000,
                    "Best Share": 1000000000.0,
                    "Diff": "100K",
                    "Diff1 Shares": 0,
                    "Difficulty Accepted": 1000000000.0,
                    "Difficulty Rejected": 1000000.0,
                    "Difficulty Stale": 0.0,
                    "Discarded": 100000,
                    "Get Failures": 3,
                    "Getworks": 9000,
                    "Has GBT": False,
                    "Has Stratum": True,
                    "Last Share Difficulty": 100000.0,
                    "Last Share Time": "0:00:02",
                    "Long Poll": "N",
                    "POOL": 0,
                    "Pool Rejected%": 0.0,
                    "Pool Stale%%": 0.0,
                    "Priority": 0,
                    "Proxy": "",
                    "Proxy Type": "",
                    "Quota": 1,
                    "Rejected": 100,
                    "Remote Failures": 0,
                    "Stale": 0,
                    "Status": "Alive",
                    "Stratum Active": True,
                    "Stratum URL": "stratum.pool.io",
                    "URL": "stratum+tcp://stratum.pool.io:3333",
                    "User": "pool_username.real_worker",
                },
                {
                    "Accepted": 10000,
                    "Best Share": 1000000000.0,
                    "Diff": "100K",
                    "Diff1 Shares": 0,
                    "Difficulty Accepted": 1000000000.0,
                    "Difficulty Rejected": 1000000.0,
                    "Difficulty Stale": 0.0,
                    "Discarded": 100000,
                    "Get Failures": 3,
                    "Getworks": 9000,
                    "Has GBT": False,
                    "Has Stratum": True,
                    "Last Share Difficulty": 100000.0,
                    "Last Share Time": "0:00:02",
                    "Long Poll": "N",
                    "POOL": 1,
                    "Pool Rejected%": 0.0,
                    "Pool Stale%%": 0.0,
                    "Priority": 0,
                    "Proxy": "",
                    "Proxy Type": "",
                    "Quota": 1,
                    "Rejected": 100,
                    "Remote Failures": 0,
                    "Stale": 0,
                    "Status": "Alive",
                    "Stratum Active": True,
                    "Stratum URL": "stratum.pool.io",
                    "URL": "stratum+tcp://stratum.pool.io:3333",
                    "User": "pool_username.real_worker",
                },
                {
                    "Accepted": 10000,
                    "Best Share": 1000000000.0,
                    "Diff": "100K",
                    "Diff1 Shares": 0,
                    "Difficulty Accepted": 1000000000.0,
                    "Difficulty Rejected": 1000000.0,
                    "Difficulty Stale": 0.0,
                    "Discarded": 100000,
                    "Get Failures": 3,
                    "Getworks": 9000,
                    "Has GBT": False,
                    "Has Stratum": True,
                    "Last Share Difficulty": 100000.0,
                    "Last Share Time": "0:00:02",
                    "Long Poll": "N",
                    "POOL": 2,
                    "Pool Rejected%": 0.0,
                    "Pool Stale%%": 0.0,
                    "Priority": 0,
                    "Proxy": "",
                    "Proxy Type": "",
                    "Quota": 1,
                    "Rejected": 100,
                    "Remote Failures": 0,
                    "Stale": 0,
                    "Status": "Alive",
                    "Stratum Active": True,
                    "Stratum URL": "stratum.pool.io",
                    "URL": "stratum+tcp://stratum.pool.io:3333",
                    "User": "pool_username.real_worker",
                },
            ],
            "id": 1,
        },
    }
}


class TestHammerMiners(unittest.IsolatedAsyncioTestCase):
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
            self.assertEqual(result.api_ver, "3.1")
            self.assertEqual(result.fw_ver, "2023-05-28 17-20-35 CST")
            self.assertEqual(result.hostname, "Hammer")
            self.assertEqual(round(result.hashrate.into(ScryptUnit.MH)), 4686)
            self.assertEqual(result.fans, [Fan(speed=4650), Fan(speed=4500)])
            self.assertEqual(result.total_chips, result.expected_chips)
