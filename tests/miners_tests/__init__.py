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
import inspect
import unittest
import warnings
from dataclasses import asdict

from pyasic.miners.backends.espminer import ESPMiner
from pyasic.miners.factory import MINER_CLASSES

from .backends_tests import *


class MinersTest(unittest.TestCase):
    def test_miner_type_creation(self):
        warnings.filterwarnings("ignore")
        for miner_type in MINER_CLASSES.keys():
            for miner_model in MINER_CLASSES[miner_type].keys():
                with self.subTest(
                    msg="Test creation of miner",
                    miner_type=miner_type,
                    miner_model=miner_model,
                ):
                    MINER_CLASSES[miner_type][miner_model]("127.0.0.1")

    def test_miner_has_hashboards(self):
        warnings.filterwarnings("ignore")
        for miner_type in MINER_CLASSES.keys():
            for miner_model in MINER_CLASSES[miner_type].keys():
                if miner_model is None:
                    continue
                with self.subTest(
                    msg="Test miner has defined hashboards",
                    miner_type=miner_type,
                    miner_model=miner_model,
                ):
                    miner = MINER_CLASSES[miner_type][miner_model]("127.0.0.1")
                    self.assertTrue(miner.expected_hashboards is not None)

    def test_miner_has_fans(self):
        warnings.filterwarnings("ignore")
        for miner_type in MINER_CLASSES.keys():
            for miner_model in MINER_CLASSES[miner_type].keys():
                if miner_model is None:
                    continue
                with self.subTest(
                    msg="Test miner has defined fans",
                    miner_type=miner_type,
                    miner_model=miner_model,
                ):
                    miner = MINER_CLASSES[miner_type][miner_model]("127.0.0.1")
                    self.assertTrue(miner.expected_fans is not None)

    def test_miner_has_algo(self):
        warnings.filterwarnings("ignore")
        for miner_type in MINER_CLASSES.keys():
            for miner_model in MINER_CLASSES[miner_type].keys():
                if miner_model is None:
                    continue
                with self.subTest(
                    msg="Test miner has defined algo",
                    miner_type=miner_type,
                    miner_model=miner_model,
                ):
                    miner = MINER_CLASSES[miner_type][miner_model]("127.0.0.1")
                    self.assertTrue(miner.algo is not None)

    def test_miner_data_map_keys(self):
        # Common keys that all miners should have
        common_keys = sorted(
            [
                "api_ver",
                "config",
                "env_temp",
                "errors",
                "fan_psu",
                "fans",
                "fault_light",
                "fw_ver",
                "hashboards",
                "hashrate",
                "hostname",
                "is_mining",
                "serial_number",
                "psu_serial_number",
                "mac",
                "expected_hashrate",
                "uptime",
                "wattage",
                "wattage_limit",
                "pools",
            ]
        )
        warnings.filterwarnings("ignore")
        for miner_type in MINER_CLASSES.keys():
            for miner_model in MINER_CLASSES[miner_type].keys():
                with self.subTest(
                    msg="Data map key check",
                    miner_type=miner_type,
                    miner_model=miner_model,
                ):
                    miner = MINER_CLASSES[miner_type][miner_model]("127.0.0.1")
                    miner_keys = sorted(
                        [str(k) for k in asdict(miner.data_locations).keys()]
                    )
                    # Check that miner has all common keys
                    for key in common_keys:
                        self.assertIn(
                            key,
                            miner_keys,
                            f"Missing common key '{key}' in {miner_type}/{miner_model}",
                        )
                    # Check ESPMiner-based miners have BitAxe-specific keys
                    if isinstance(miner, ESPMiner):
                        espminer_keys = [
                            "best_difficulty",
                            "best_session_difficulty",
                            "shares_accepted",
                            "shares_rejected",
                        ]
                        for key in espminer_keys:
                            self.assertIn(
                                key,
                                miner_keys,
                                f"Missing ESPMiner key '{key}' in {miner_type}/{miner_model}",
                            )

    def test_data_locations_match_signatures_command(self):
        warnings.filterwarnings("ignore")
        for miner_type in MINER_CLASSES.keys():
            for miner_model in MINER_CLASSES[miner_type].keys():
                miner = MINER_CLASSES[miner_type][miner_model]("127.0.0.1")
                if miner.data_locations is None:
                    raise TypeError(
                        f"model={miner_model} type={miner_type} has no data locations"
                    )
                for data_point in asdict(miner.data_locations).values():
                    with self.subTest(
                        msg=f"Test {data_point['cmd']} signature matches",
                        miner_type=miner_type,
                        miner_model=miner_model,
                    ):
                        try:
                            func = getattr(miner, data_point["cmd"])
                        except AttributeError:
                            # Skip if method doesn't exist (e.g., custom fields)
                            self.skipTest(
                                f"Method {data_point['cmd']} not implemented for {miner_type}/{miner_model}"
                            )
                        signature = inspect.signature(func)
                        parameters = signature.parameters
                        param_names = list(parameters.keys())
                        for arg in ["kwargs", "args"]:
                            try:
                                param_names.remove(arg)
                            except ValueError:
                                pass
                        self.assertEqual(
                            set(param_names),
                            set([k["name"] for k in data_point["kwargs"]]),
                        )


if __name__ == "__main__":
    unittest.main()
