# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------
import asyncio
import inspect
import sys
import unittest
import warnings

from pyasic.miners._backends import CGMiner  # noqa
from pyasic.miners.base import BaseMiner
from pyasic.miners.miner_factory import MINER_CLASSES, MinerFactory


class MinersTest(unittest.TestCase):
    def test_miner_model_creation(self):
        warnings.filterwarnings("ignore")
        for miner_model in MINER_CLASSES.keys():
            for miner_api in MINER_CLASSES[miner_model].keys():
                with self.subTest(
                    msg=f"Creation of miner using model={miner_model}, api={miner_api}",
                    miner_model=miner_model,
                    miner_api=miner_api,
                ):
                    miner = MINER_CLASSES[miner_model][miner_api]("0.0.0.0")
                    self.assertTrue(
                        isinstance(miner, MINER_CLASSES[miner_model][miner_api])
                    )

    def test_miner_backend_backup_creation(self):
        warnings.filterwarnings("ignore")

        backends = inspect.getmembers(
            sys.modules["pyasic.miners._backends"], inspect.isclass
        )
        for backend in backends:
            miner_class = backend[1]
            with self.subTest(miner_class=miner_class):
                miner = miner_class("0.0.0.0")
                self.assertTrue(isinstance(miner, miner_class))

    def test_miner_type_creation_failure(self):
        warnings.filterwarnings("ignore")

        backends = inspect.getmembers(
            sys.modules["pyasic.miners._types"], inspect.isclass
        )
        for backend in backends:
            miner_class = backend[1]
            with self.subTest(miner_class=miner_class):
                with self.assertRaises(TypeError):
                    miner_class("0.0.0.0")
        with self.assertRaises(TypeError):
            BaseMiner("0.0.0.0")

    def test_miner_comparisons(self):
        miner_1 = CGMiner("1.1.1.1")
        miner_2 = CGMiner("2.2.2.2")
        miner_3 = CGMiner("1.1.1.1")
        self.assertEqual(miner_1, miner_3)
        self.assertGreater(miner_2, miner_1)
        self.assertLess(miner_3, miner_2)


class MinerFactoryTest(unittest.TestCase):
    def test_miner_factory_creation(self):
        warnings.filterwarnings("ignore")

        self.assertDictEqual(MinerFactory().miners, {})
        miner_factory = MinerFactory()
        self.assertIs(MinerFactory(), miner_factory)

    def test_get_miner_generator(self):
        async def _coro():
            gen = MinerFactory().get_miner_generator([])
            miners = []
            async for miner in gen:
                miners.append(miner)
            return miners

        _miners = asyncio.run(_coro())
        self.assertListEqual(_miners, [])

    def test_miner_selection(self):
        warnings.filterwarnings("ignore")

        for miner_model in MINER_CLASSES.keys():
            with self.subTest():
                miner = MinerFactory()._select_miner_from_classes(
                    "0.0.0.0", miner_model, None, None
                )
                self.assertIsInstance(miner, BaseMiner)
        for api in ["BOSMiner+", "BOSMiner", "CGMiner", "BTMiner", "BMMiner"]:
            with self.subTest():
                miner = MinerFactory()._select_miner_from_classes(
                    "0.0.0.0", None, api, None
                )
                self.assertIsInstance(miner, BaseMiner)

        with self.subTest():
            miner = MinerFactory()._select_miner_from_classes(
                "0.0.0.0", "ANTMINER S17+", "Fake API", None
            )
            self.assertIsInstance(miner, BaseMiner)

        with self.subTest():
            miner = MinerFactory()._select_miner_from_classes(
                "0.0.0.0", "M30S", "BTMiner", "G20"
            )
            self.assertIsInstance(miner, BaseMiner)

    def test_validate_command(self):
        bad_test_data_returns = [
            {},
            {
                "cmd": [
                    {
                        "STATUS": [
                            {"STATUS": "E", "Msg": "Command failed for some reason."}
                        ]
                    }
                ]
            },
            {"STATUS": "E", "Msg": "Command failed for some reason."},
            {
                "STATUS": [{"STATUS": "E", "Msg": "Command failed for some reason."}],
                "id": 1,
            },
        ]
        for data in bad_test_data_returns:
            with self.subTest():

                async def _coro(miner_ret):
                    _data = await MinerFactory()._validate_command(miner_ret)
                    return _data

                ret = asyncio.run(_coro(data))
                self.assertFalse(ret[0])

        good_test_data_returns = [
            {
                "STATUS": [{"STATUS": "S", "Msg": "Yay! Command succeeded."}],
                "id": 1,
            },
        ]
        for data in good_test_data_returns:
            with self.subTest():

                async def _coro(miner_ret):
                    _data = await MinerFactory()._validate_command(miner_ret)
                    return _data

                ret = asyncio.run(_coro(data))
                self.assertTrue(ret[0])


if __name__ == "__main__":
    unittest.main()
