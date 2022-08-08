#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import unittest

from pyasic.miners.miner_factory import MINER_CLASSES

import inspect
import sys


class MinersTest(unittest.TestCase):
    def test_miner_model_creation(self):
        for miner_model in MINER_CLASSES.keys():
            for miner_api in MINER_CLASSES[miner_model].keys():
                with self.subTest(miner_model=miner_model, miner_api=miner_api):
                    miner = MINER_CLASSES[miner_model][miner_api]("0.0.0.0")
                    self.assertTrue(
                        isinstance(miner, MINER_CLASSES[miner_model][miner_api])
                    )

    def test_miner_backend_backup_creation(self):
        backends = inspect.getmembers(
            sys.modules["pyasic.miners._backends"], inspect.isclass
        )
        for backend in backends:
            miner_class = backend[1]
            with self.subTest(miner_class=miner_class):
                miner = miner_class("0.0.0.0")
                self.assertTrue(isinstance(miner, miner_class))

    def test_miner_type_creation_failure(self):
        backends = inspect.getmembers(
            sys.modules["pyasic.miners._types"], inspect.isclass
        )
        for backend in backends:
            miner_class = backend[1]
            with self.subTest(miner_class=miner_class):
                with self.assertRaises(TypeError):
                    miner_class("0.0.0.0")


if __name__ == "__main__":
    unittest.main()
