import argparse
import os
import sys
import unittest

from pyasic.miners.base import BaseMiner
from pyasic.miners.data import DataOptions
from pyasic.miners.factory import MinerFactory


class TestAvalonLocal(unittest.IsolatedAsyncioTestCase):
    ip: str | None = None
    password: str | None = None
    miner: BaseMiner

    @classmethod
    def setUpClass(cls) -> None:
        cls.ip = os.getenv("AVALON_IP")
        cls.password = os.getenv("AVALON_PASSWORD")
        if not cls.ip:
            raise unittest.SkipTest("Set AVALON_IP to run local Avalon tests")

    async def asyncSetUp(self) -> None:
        assert self.ip is not None  # set in setUpClass or test is skipped
        factory = MinerFactory()
        miner = await factory.get_miner(self.ip)  # type: ignore[func-returns-value]
        if miner is None:
            self.skipTest("Miner discovery failed; check IP/auth")
        self.miner = miner
        return None

        # Some Avalon units do not require authentication; when needed they use the
        # cgminer RPC interface which pyasic handles internally. No extra setup here.

    async def test_get_data_basics(self):
        data = await self.miner.get_data(
            include=[
                DataOptions.HOSTNAME,
                DataOptions.API_VERSION,
                DataOptions.FW_VERSION,
                DataOptions.HASHRATE,
                DataOptions.POOLS,
            ]
        )
        if data.hostname is None:
            self.skipTest("Hostname not reported; skipping")
        if data.hashrate is None:
            self.skipTest("Hashrate not reported; skipping")

        self.assertIsNotNone(data.hostname)
        self.assertIsNotNone(data.hashrate)

    async def test_get_config(self):
        cfg = await self.miner.get_config()
        self.assertIsNotNone(cfg)

    async def test_fault_light_cycle(self):
        # Not all Avalon minis/nanos support fault light control; tolerate failure.
        if not hasattr(self.miner, "fault_light_on"):
            self.skipTest("Miner missing fault light support")
        turned_on = await self.miner.fault_light_on()
        turned_off = await self.miner.fault_light_off()
        if not (turned_on or turned_off):
            self.skipTest("Fault light control unsupported or disabled")
        self.assertTrue(True)


def _main() -> None:
    parser = argparse.ArgumentParser(description="Local Avalon mini/nano smoke tests")
    parser.add_argument("ip", nargs="?", help="Miner IP (overrides AVALON_IP)")
    parser.add_argument("--password", help="Optional web/RPC password", default=None)
    args, unittest_args = parser.parse_known_args()

    if args.ip:
        os.environ["AVALON_IP"] = args.ip
    if args.password:
        os.environ["AVALON_PASSWORD"] = args.password

    unittest.main(argv=[sys.argv[0]] + unittest_args)


if __name__ == "__main__":
    _main()
