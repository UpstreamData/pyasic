import argparse
import os
import sys
import unittest

from pyasic.miners.base import BaseMiner
from pyasic.miners.data import DataOptions
from pyasic.miners.factory import MinerFactory
from pyasic.miners.fluminer import FluminerT3
from pyasic.web.fluminer import FluminerWebAPI


class TestFluminerLocal(unittest.IsolatedAsyncioTestCase):
    ip: str | None = None
    miner: BaseMiner

    @classmethod
    def setUpClass(cls) -> None:
        cls.ip = os.getenv("FLUMINER_IP")
        if not cls.ip:
            raise unittest.SkipTest("Set FLUMINER_IP to run local Fluminer tests")

    async def asyncSetUp(self) -> None:
        if self.ip is None:
            self.skipTest("Set FLUMINER_IP to run local Fluminer tests")
        factory = MinerFactory()
        miner = await factory.get_miner(self.ip)  # type: ignore[func-returns-value]
        if miner is None:
            self.skipTest("Miner discovery failed; check IP")
        self.miner = miner
        return None

    async def test_discovery_detects_fluminer_t3(self) -> None:
        self.assertIsInstance(self.miner, FluminerT3)

    async def test_get_data_basics(self) -> None:
        data = await self.miner.get_data(
            include=[
                DataOptions.SERIAL_NUMBER,
                DataOptions.FW_VERSION,
                DataOptions.HASHRATE,
                DataOptions.WATTAGE,
                DataOptions.FANS,
                DataOptions.HASHBOARDS,
                DataOptions.POOLS,
                DataOptions.IS_MINING,
            ]
        )

        if data.serial_number is None:
            self.skipTest("Serial number not reported; skipping")
        if data.fw_ver is None:
            self.skipTest("FW version not reported; skipping")
        if data.hashrate is None:
            self.skipTest("Hashrate not reported; skipping")
        if data.wattage is None:
            self.skipTest("Wattage not reported; skipping")
        if data.is_mining is None:
            self.skipTest("Mining status not reported; skipping")
        if data.fans is None or len(data.fans) == 0:
            self.skipTest("Fans not reported; skipping")
        if data.hashboards is None or len(data.hashboards) == 0:
            self.skipTest("Hashboards not reported; skipping")
        if data.pools is None or len(data.pools) == 0:
            self.skipTest("Pools not reported; skipping")

        self.assertEqual(type(self.miner).__name__, "FluminerT3")
        self.assertEqual(data.model, "T3")
        self.assertIsNotNone(data.serial_number)
        self.assertIsNotNone(data.fw_ver)
        self.assertIsNotNone(data.hashrate)
        self.assertIsNotNone(data.wattage)
        self.assertIsNotNone(data.is_mining)
        self.assertEqual(len(data.fans), 4)
        self.assertEqual(len(data.hashboards), 1)
        self.assertEqual(data.hashboards[0].expected_chips, 96)
        self.assertIsNone(data.hashboards[0].chips)
        self.assertGreaterEqual(len(data.pools), 1)

    async def test_get_config_returns_configured_pools(self) -> None:
        cfg = await self.miner.get_config()
        self.assertGreaterEqual(len(cfg.pools.groups), 1)
        self.assertGreaterEqual(len(cfg.pools.groups[0].pools), 1)

    async def test_native_web_api_read_only_endpoints(self) -> None:
        web = getattr(self.miner, "web", None)
        if web is None or not isinstance(web, FluminerWebAPI):
            self.skipTest("No Fluminer web client available")

        overview = await web.overview()
        summary = await web.summary()
        pools = await web.pools()

        self.assertEqual(overview.get("code"), 0)
        self.assertEqual(summary.get("code"), 0)
        self.assertEqual(pools.get("code"), 0)
        self.assertIn("minerInfo", overview.get("data", {}))
        self.assertIn("summary", summary.get("data", {}))
        self.assertIn("pools", pools.get("data", {}))


def _main() -> None:
    parser = argparse.ArgumentParser(description="Local Fluminer T3 smoke tests")
    parser.add_argument("ip", nargs="?", help="Miner IP (overrides FLUMINER_IP)")
    args, unittest_args = parser.parse_known_args()

    if args.ip:
        os.environ["FLUMINER_IP"] = args.ip

    unittest.main(argv=[sys.argv[0]] + unittest_args)


if __name__ == "__main__":
    _main()
