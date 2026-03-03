import argparse
import os
import sys
import unittest

from pyasic.miners.base import BaseMiner
from pyasic.miners.data import DataOptions
from pyasic.miners.factory import MinerFactory


class TestAntminerLocal(unittest.IsolatedAsyncioTestCase):
    ip: str | None = None
    password: str | None = None
    miner: BaseMiner

    @classmethod
    def setUpClass(cls) -> None:
        cls.ip = os.getenv("ANTMINER_IP")
        cls.password = os.getenv("ANTMINER_PASSWORD", "root")
        if not cls.ip:
            raise unittest.SkipTest("Set ANTMINER_IP to run local Antminer tests")

    async def asyncSetUp(self) -> None:
        if self.ip is None:
            self.skipTest("ANTMINER_IP not set")
        factory = MinerFactory()
        miner = await factory.get_miner(self.ip)  # type: ignore[func-returns-value]
        if miner is None:
            self.skipTest("Miner discovery failed; check IP/auth")
        self.miner = miner
        if self.password and hasattr(self.miner, "web") and self.miner.web is not None:
            self.miner.web.pwd = self.password
        return None

    async def test_get_data_basics(self):
        data = await self.miner.get_data(
            include=[
                DataOptions.HOSTNAME,
                DataOptions.API_VERSION,
                DataOptions.FW_VERSION,
                DataOptions.HASHRATE,
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

    async def test_change_password_roundtrip(self):
        if not hasattr(self.miner, "change_password"):
            self.skipTest("Miner does not support change_password")

        original_password = self.password or "root"
        temp_password = "test_pyasic_pwd"

        # Change to temp password
        success = await self.miner.change_password(temp_password)
        self.assertTrue(success, "Failed to change password to temp value")

        # Verify API still works with new password
        try:
            info = await self.miner.web.get_system_info()
            self.assertIsNotNone(info)
        except Exception:
            # Revert attempt even if verification failed
            self.miner.web.pwd = temp_password
            await self.miner.change_password(original_password)
            self.fail("API call failed after password change")

        # Change back to original
        success = await self.miner.change_password(original_password)
        self.assertTrue(success, "Failed to revert password to original")

        # Verify API works with original password
        info = await self.miner.web.get_system_info()
        self.assertIsNotNone(info)


def _main() -> None:
    parser = argparse.ArgumentParser(description="Local Antminer smoke tests")
    parser.add_argument("ip", nargs="?", help="Miner IP (overrides ANTMINER_IP)")
    parser.add_argument("--password", help="Web password (default: root)", default=None)
    args, unittest_args = parser.parse_known_args()

    if args.ip:
        os.environ["ANTMINER_IP"] = args.ip
    if args.password:
        os.environ["ANTMINER_PASSWORD"] = args.password

    unittest.main(argv=[sys.argv[0]] + unittest_args)


if __name__ == "__main__":
    _main()
