import unittest
from unittest.mock import AsyncMock

from pyasic.errors import APIError
from pyasic.miners.backends.btminer import BTMinerV3


class TestBTMinerV3ErrorMapping(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.miner = BTMinerV3(ip="10.1.10.24")

    async def test_get_errors_maps_device_info_codes(self):
        rpc_get_device_info = {
            "msg": {
                "error-code": [
                    "2010",
                    541,
                    {"541": "Slot 1 error reading chip id.", "reason": "hashboard"},
                    {"5032": "Slot 2 voltage abnormal"},
                    "not-a-code",
                    None,
                ]
            }
        }

        errors = await self.miner._get_errors(rpc_get_device_info=rpc_get_device_info)
        codes = [error.error_code for error in errors]

        self.assertEqual(codes, [541, 2010, 5032])

    async def test_get_errors_ignores_non_list_error_code_payload(self):
        rpc_get_device_info = {"msg": {"error-code": "btminer process is down err"}}

        errors = await self.miner._get_errors(rpc_get_device_info=rpc_get_device_info)

        self.assertEqual(errors, [])

    async def test_get_errors_returns_empty_on_rpc_api_error(self):
        self.miner.rpc = AsyncMock()
        self.miner.rpc.get_device_info = AsyncMock(side_effect=APIError("rpc failed"))

        errors = await self.miner._get_errors()

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
