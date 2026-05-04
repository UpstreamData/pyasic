import unittest

from pyasic.miners.backends.fluminer import Fluminer
from pyasic.miners.factory import MinerFactory, MinerTypes
from pyasic.miners.fluminer import FluminerT3

OVERVIEW = {
    "code": 0,
    "data": {
        "minerInfo": {
            "model": "T3",
            "sn": "HYT360202C10H12S11B0300211",
            "minerVersion": "V1.12",
            "macAddress": "70:69:79:31:1e:80",
        }
    },
}

SUMMARY = {
    "code": 0,
    "data": {
        "summary": [
            {
                "pool": "stratum.braiins.com",
                "poolAlive": "1",
                "port": "3333",
                "hrt": "111455.52",
                "acc": "10900",
                "rej": "0",
                "temp": "31|38",
                "fan": "3524|3583|3583|3613",
                "voltage": "26.38",
                "power": "1723.41",
                "uptime": "98063",
                "status": "OK",
                "model": "T3",
            }
        ]
    },
}

POOLS = {
    "code": 0,
    "data": {
        "pools": [
            {
                "url": "stratum2+tcp://stratum.braiins.com:3333/pubkey",
                "user": "worker",
                "pass": "123",
            },
            {
                "url": "stratum+tcp://backup.example.com:3333",
                "user": "worker",
                "pass": "123",
            },
        ]
    },
}


class TestFluminer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.miner = FluminerT3("127.0.0.1")

    async def test_summary_data(self):
        self.assertEqual(
            await self.miner._get_serial_number(OVERVIEW),
            OVERVIEW["data"]["minerInfo"]["sn"],
        )
        self.assertEqual(await self.miner._get_mac(OVERVIEW), "70:69:79:31:1E:80")
        self.assertEqual(await self.miner._get_fw_ver(OVERVIEW), "V1.12")
        self.assertEqual(
            round(float(await self.miner._get_hashrate(SUMMARY)), 3), 111.456
        )
        self.assertEqual(await self.miner._get_wattage(SUMMARY), 1723)
        self.assertEqual(await self.miner._get_uptime(SUMMARY), 98063)
        self.assertTrue(await self.miner._is_mining(SUMMARY))

    async def test_fans_and_hashboards(self):
        fans = await self.miner._get_fans(SUMMARY)
        self.assertEqual([fan.speed for fan in fans], [3524, 3583, 3583, 3613])

        hashboards = await self.miner._get_hashboards(SUMMARY)
        self.assertEqual(len(hashboards), 1)
        self.assertFalse(hashboards[0].missing)
        self.assertEqual(hashboards[0].temp, 31)
        self.assertEqual(hashboards[0].chip_temp, 38)
        self.assertEqual(hashboards[0].expected_chips, 96)
        self.assertIsNone(hashboards[0].chips)
        self.assertEqual(hashboards[0].voltage, 26.38)

    async def test_empty_summary_preserves_expected_hashboard_placeholder(self):
        hashboards = await self.miner._get_hashboards({"code": 0, "data": {}})

        self.assertEqual(len(hashboards), 1)
        self.assertTrue(hashboards[0].missing)
        self.assertIsNone(hashboards[0].hashrate)

    async def test_partial_fan_data_preserves_expected_fan_count(self):
        summary = {
            **SUMMARY,
            "data": {
                "summary": [{**SUMMARY["data"]["summary"][0], "fan": "3524|3583"}]
            },
        }

        fans = await self.miner._get_fans(summary)

        self.assertEqual(len(fans), 4)
        self.assertEqual([fan.speed for fan in fans], [3524, 3583, None, None])

    async def test_pools(self):
        pools = await self.miner._get_pools(web_summary=SUMMARY, web_pools=POOLS)

        self.assertEqual(len(pools), 2)
        self.assertTrue(pools[0].active)
        self.assertTrue(pools[0].alive)
        self.assertEqual(pools[0].accepted, 10900)
        self.assertEqual(pools[0].rejected, 0)
        self.assertFalse(pools[1].active)
        self.assertIsNone(pools[1].accepted)

    async def test_active_pool_matching_requires_exact_host_and_port(self):
        pools = await self.miner._get_pools(
            web_summary=SUMMARY,
            web_pools={
                "code": 0,
                "data": {
                    "pools": [
                        {
                            "url": "stratum+tcp://not-stratum.braiins.com:3333",
                            "user": "worker",
                            "pass": "123",
                        },
                        {
                            "url": "stratum+tcp://stratum.braiins.com:333",
                            "user": "worker",
                            "pass": "123",
                        },
                        {
                            "url": "stratum+tcp://stratum.braiins.com:3333",
                            "user": "worker",
                            "pass": "123",
                        },
                    ]
                },
            },
        )

        self.assertEqual([pool.active for pool in pools], [False, False, True])

    async def test_malformed_payloads_return_empty_data(self):
        self.assertIsNone(
            await self.miner._get_serial_number({"code": 0, "data": None})
        )
        self.assertIsNone(
            await self.miner._get_hashrate({"code": 0, "data": {"summary": [None]}})
        )
        self.assertEqual(
            await self.miner._get_pools(
                web_summary=SUMMARY,
                web_pools={
                    "code": 0,
                    "data": {
                        "pools": [
                            None,
                            {"url": "not-a-supported-scheme://pool:3333"},
                            {"url": ""},
                        ]
                    },
                },
            ),
            [],
        )

    async def test_unknown_fluminer_has_no_expected_hashboards(self):
        miner = Fluminer("127.0.0.1")

        self.assertEqual(await miner._get_hashboards(SUMMARY), [])

    def test_factory_detects_fluminer_before_generic_miner_ui(self):
        self.assertEqual(
            MinerFactory._parse_web_type(
                "<html><title>Fluminer</title>Miner UI</html>",
                type("Resp", (), {"status_code": 200, "headers": {}, "history": []})(),
            ),
            MinerTypes.FLUMINER,
        )


if __name__ == "__main__":
    unittest.main()
