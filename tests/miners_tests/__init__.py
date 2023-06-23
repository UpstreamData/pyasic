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

from pyasic.miners.backends import CGMiner  # noqa
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
                    miner = MINER_CLASSES[miner_model][miner_api]("127.0.0.1")
                    self.assertTrue(
                        isinstance(miner, MINER_CLASSES[miner_model][miner_api])
                    )


if __name__ == "__main__":
    unittest.main()
