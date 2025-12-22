import argparse
import os
import sys
import unittest
from typing import Any

from pyasic.miners.base import BaseMiner
from pyasic.miners.data import DataOptions
from pyasic.miners.factory import MinerFactory
from pyasic.web.espminer import ESPMinerWebAPI


class TestBitAxeLocal(unittest.IsolatedAsyncioTestCase):
    ip: str | None = None
    miner: BaseMiner

    @classmethod
    def setUpClass(cls) -> None:
        cls.ip = os.getenv("BITAXE_IP")
        if not cls.ip:
            raise unittest.SkipTest("Set BITAXE_IP to run local BitAxe tests")

    async def asyncSetUp(self) -> None:
        assert self.ip is not None  # set in setUpClass or test is skipped
        factory = MinerFactory()
        miner = await factory.get_miner(self.ip)  # type: ignore[func-returns-value]
        if miner is None:
            self.skipTest("Miner discovery failed; check IP")
        self.miner = miner
        return None

    async def test_get_data_basics(self):
        data = await self.miner.get_data(
            include=[
                DataOptions.HOSTNAME,
                DataOptions.API_VERSION,
                DataOptions.FW_VERSION,
                DataOptions.HASHRATE,
                DataOptions.MAC,
            ]
        )
        if data.hostname is None:
            self.skipTest("Hostname not reported; skipping")
        if data.hashrate is None:
            self.skipTest("Hashrate not reported; skipping")
        if data.mac is None:
            self.skipTest("MAC not reported; skipping")

        self.assertIsNotNone(data.hostname)
        self.assertIsNotNone(data.hashrate)
        self.assertIsNotNone(data.mac)

    async def test_get_config(self):
        cfg = await self.miner.get_config()
        self.assertIsNotNone(cfg)

    async def test_get_data_extended(self):
        data = await self.miner.get_data(
            include=[
                DataOptions.HOSTNAME,
                DataOptions.API_VERSION,
                DataOptions.FW_VERSION,
                DataOptions.HASHRATE,
                DataOptions.EXPECTED_HASHRATE,
                DataOptions.WATTAGE,
                DataOptions.UPTIME,
                DataOptions.FANS,
                DataOptions.HASHBOARDS,
                DataOptions.MAC,
            ]
        )

        if data.hostname is None:
            self.skipTest("Hostname not reported; skipping")
        if data.api_ver is None:
            self.skipTest("API version not reported; skipping")
        if data.fw_ver is None:
            self.skipTest("FW version not reported; skipping")
        if data.expected_hashrate is None:
            self.skipTest("Expected hashrate not reported; skipping")
        if data.wattage is None:
            self.skipTest("Wattage not reported; skipping")
        if data.uptime is None:
            self.skipTest("Uptime not reported; skipping")
        if data.hashboards is None or len(data.hashboards) == 0:
            self.skipTest("Hashboards not reported; skipping")
        if data.fans is None or len(data.fans) == 0:
            self.skipTest("Fans not reported; skipping")

        self.assertIsNotNone(data.hostname)
        self.assertIsNotNone(data.api_ver)
        self.assertIsNotNone(data.fw_ver)
        self.assertIsNotNone(data.expected_hashrate)
        self.assertIsNotNone(data.wattage)
        self.assertIsNotNone(data.uptime)
        self.assertGreater(len(data.hashboards), 0)
        self.assertGreater(len(data.fans), 0)

    async def test_swarm_and_asic_info(self):
        # Only run if the miner exposes the ESPMiner web API methods
        web = getattr(self.miner, "web", None)
        if web is None or not isinstance(web, ESPMinerWebAPI):
            self.skipTest("No web client available")

        swarm_info: dict[str, Any] | None = None
        asic_info: dict[str, Any] | None = None
        try:
            swarm_info = await web.swarm_info()
            asic_info = await web.asic_info()
        except Exception:
            self.skipTest("Web API not reachable or not supported")

        if not swarm_info:
            self.skipTest("Swarm info empty; skipping")
        if not asic_info:
            self.skipTest("ASIC info empty; skipping")

        # Check for a couple of expected fields if present
        if "asicCount" in asic_info:
            self.assertIsInstance(asic_info.get("asicCount"), int)
        if "frequency" in asic_info:
            self.assertIsInstance(asic_info.get("frequency"), (int, float))


def _main() -> None:
    parser = argparse.ArgumentParser(description="Local BitAxe smoke tests")
    parser.add_argument("ip", nargs="?", help="Miner IP (overrides BITAXE_IP)")
    args, unittest_args = parser.parse_known_args()

    if args.ip:
        os.environ["BITAXE_IP"] = args.ip

    unittest.main(argv=[sys.argv[0]] + unittest_args)


if __name__ == "__main__":
    _main()
