"""Tests for BTMiner V3 PSU fan speed parsing."""

import unittest

from pyasic.miners.backends.btminer import BTMinerV3


class TestBTMinerV3PSUFans(unittest.IsolatedAsyncioTestCase):
    async def test_get_psu_fans_keeps_int_value(self):
        miner = BTMinerV3("127.0.0.1")

        fans = await miner._get_psu_fans(
            rpc_get_device_info={"msg": {"power": {"fanspeed": 6000}}}
        )

        self.assertEqual(len(fans), 1)
        self.assertEqual(fans[0].speed, 6000)

    async def test_get_psu_fans_converts_float_value(self):
        miner = BTMinerV3("127.0.0.1")

        fans = await miner._get_psu_fans(
            rpc_get_device_info={"msg": {"power": {"fanspeed": 26.1}}}
        )

        self.assertEqual(len(fans), 1)
        self.assertEqual(fans[0].speed, 26)

    async def test_get_psu_fans_converts_string_float_value(self):
        miner = BTMinerV3("127.0.0.1")

        fans = await miner._get_psu_fans(
            rpc_get_device_info={"msg": {"power": {"fanspeed": "25.7"}}}
        )

        self.assertEqual(len(fans), 1)
        self.assertEqual(fans[0].speed, 26)

    async def test_get_psu_fans_invalid_value_returns_empty(self):
        miner = BTMinerV3("127.0.0.1")

        fans = await miner._get_psu_fans(
            rpc_get_device_info={"msg": {"power": {"fanspeed": "n/a"}}}
        )

        self.assertEqual(fans, [])
