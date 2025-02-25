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
from typing import List, Union

from pyasic.errors import APIError
from pyasic.miners import AnyMiner
from pyasic.miners.backends import AntminerModern, BOSMiner, BTMiner
from pyasic.miners.device.models import (
    S9,
    S17,
    T17,
    S17e,
    S17Plus,
    S17Pro,
    T17e,
    T17Plus,
)

FAN_USAGE = 50  # 50 W per fan


class MinerLoadBalancer:
    """A load balancer for miners.  Can be passed a list of `AnyMiner`, or a list of phases (lists of `AnyMiner`)."""

    def __init__(
        self,
        phases: Union[List[List[AnyMiner]], None] = None,
    ):
        self.phases = [_MinerPhaseBalancer(phase) for phase in phases]

    async def balance(self, wattage: int) -> int:
        phase_wattage = wattage // len(self.phases)
        setpoints = await asyncio.gather(
            *[phase.get_balance_setpoints(phase_wattage) for phase in self.phases]
        )
        tasks = []
        total_wattage = 0
        for setpoint in setpoints:
            wattage_set = 0
            for miner in setpoint:
                if setpoint[miner]["set"] == "on":
                    wattage_set += setpoint[miner]["max"]
                    tasks.append(setpoint[miner]["miner"].resume_mining())
                elif setpoint[miner]["set"] == "off":
                    wattage_set += setpoint[miner]["min"]
                    tasks.append(setpoint[miner]["miner"].stop_mining())
                else:
                    wattage_set += setpoint[miner]["set"]
                    tasks.append(
                        setpoint[miner]["miner"].set_power_limit(setpoint[miner]["set"])
                    )
            total_wattage += wattage_set
        await asyncio.gather(*tasks)
        return total_wattage


class _MinerPhaseBalancer:
    def __init__(self, miners: List[AnyMiner]):
        self.miners = {
            str(miner.ip): {
                "miner": miner,
                "set": 0,
                "min": miner.expected_fans * FAN_USAGE,
            }
            for miner in miners
        }
        for miner in miners:
            if (
                isinstance(miner, BTMiner)
                and not (miner.raw_model.startswith("M2") if miner.raw_model else True)
            ) or isinstance(miner, BOSMiner):
                if isinstance(miner, S9):
                    self.miners[str(miner.ip)]["tune"] = True
                    self.miners[str(miner.ip)]["shutdown"] = True
                    self.miners[str(miner.ip)]["max"] = 1400
                elif True in [
                    isinstance(miner, x)
                    for x in [S17, S17Plus, S17Pro, S17e, T17, T17Plus, T17e]
                ]:
                    self.miners[str(miner.ip)]["tune"] = True
                    self.miners[str(miner.ip)]["shutdown"] = True
                    self.miners[str(miner.ip)]["max"] = 2400
                else:
                    self.miners[str(miner.ip)]["tune"] = True
                    self.miners[str(miner.ip)]["shutdown"] = True
                    self.miners[str(miner.ip)]["max"] = 3600
            elif isinstance(miner, AntminerModern):
                self.miners[str(miner.ip)]["tune"] = False
                self.miners[str(miner.ip)]["shutdown"] = True
                self.miners[str(miner.ip)]["max"] = 3600
            elif isinstance(miner, BTMiner):
                self.miners[str(miner.ip)]["tune"] = False
                self.miners[str(miner.ip)]["shutdown"] = True
                self.miners[str(miner.ip)]["max"] = 3600
                if miner.raw_model:
                    if miner.raw_model.startswith("M2"):
                        self.miners[str(miner.ip)]["tune"] = False
                        self.miners[str(miner.ip)]["shutdown"] = True
                        self.miners[str(miner.ip)]["max"] = 2400
            else:
                self.miners[str(miner.ip)]["tune"] = False
                self.miners[str(miner.ip)]["shutdown"] = False
                self.miners[str(miner.ip)]["max"] = 3600
                self.miners[str(miner.ip)]["min"] = 3600

    async def balance(self, wattage: int) -> int:
        setpoint = await self.get_balance_setpoints(wattage)
        wattage_set = 0
        tasks = []
        for miner in setpoint:
            if setpoint[miner]["set"] == "on":
                wattage_set += setpoint[miner]["max"]
                tasks.append(setpoint[miner]["miner"].resume_mining())
            elif setpoint[miner]["set"] == "off":
                wattage_set += setpoint[miner]["min"]
                tasks.append(setpoint[miner]["miner"].stop_mining())
            else:
                wattage_set += setpoint[miner]["set"]
                tasks.append(
                    setpoint[miner]["miner"].set_power_limit(setpoint[miner]["set"])
                )
        await asyncio.gather(*tasks)
        return wattage_set

    async def get_balance_setpoints(self, wattage: int) -> dict:
        # gather data needed to optimize shutdown only miners
        dp = ["hashrate", "wattage", "wattage_limit", "hashboards"]
        data = await asyncio.gather(
            *[
                self.miners[miner]["miner"].get_data(data_to_get=dp)
                for miner in self.miners
            ]
        )
        pct_expected_list = [d.percent_ideal for d in data]
        pct_ideal = 0
        if len(pct_expected_list) > 0:
            pct_ideal = sum(pct_expected_list) / len(pct_expected_list)

        wattage = round(wattage * 1 / (pct_ideal / 100))

        for data_point in data:
            if (not self.miners[data_point.ip]["tune"]) and (
                not self.miners[data_point.ip]["shutdown"]
            ):
                # cant do anything with it so need to find a semi-accurate power limit
                if data_point.wattage_limit is not None:
                    self.miners[data_point.ip]["max"] = int(data_point.wattage_limit)
                    self.miners[data_point.ip]["min"] = int(data_point.wattage_limit)
                elif data_point.wattage is not None:
                    self.miners[data_point.ip]["max"] = int(data_point.wattage)
                    self.miners[data_point.ip]["min"] = int(data_point.wattage)

        max_tune_wattage = sum(
            [miner["max"] for miner in self.miners.values() if miner["tune"]]
        )
        max_shutdown_wattage = sum(
            [
                miner["max"]
                for miner in self.miners.values()
                if (not miner["tune"]) and (miner["shutdown"])
            ]
        )
        max_other_wattage = sum(
            [
                miner["max"]
                for miner in self.miners.values()
                if (not miner["tune"]) and (not miner["shutdown"])
            ]
        )
        min_tune_wattage = sum(
            [miner["min"] for miner in self.miners.values() if miner["tune"]]
        )
        min_shutdown_wattage = sum(
            [
                miner["min"]
                for miner in self.miners.values()
                if (not miner["tune"]) and (miner["shutdown"])
            ]
        )
        # min_other_wattage = sum(
        #     [
        #         miner["min"]
        #         for miner in self.miners.values()
        #         if (not miner["tune"]) and (not miner["shutdown"])
        #     ]
        # )

        # make sure wattage isnt set too high
        if wattage > (max_tune_wattage + max_shutdown_wattage + max_other_wattage):
            raise APIError(
                f"Wattage setpoint is too high, setpoint: {wattage}W, max: {max_tune_wattage + max_shutdown_wattage + max_other_wattage}W"
            )

        # should now know wattage limits and which can be tuned/shutdown
        # check if 1/2 max of the miners which can be tuned is low enough
        if (max_tune_wattage / 2) + max_shutdown_wattage + max_other_wattage < wattage:
            useable_wattage = wattage - (max_other_wattage + max_shutdown_wattage)
            useable_miners = len(
                [m for m in self.miners.values() if (m["set"] == 0) and (m["tune"])]
            )
            if not useable_miners == 0:
                watts_per_miner = useable_wattage // useable_miners
                # loop through and set useable miners to wattage
                for miner in self.miners:
                    if (self.miners[miner]["set"] == 0) and (
                        self.miners[miner]["tune"]
                    ):
                        self.miners[miner]["set"] = watts_per_miner
                    elif self.miners[miner]["set"] == 0 and (
                        self.miners[miner]["shutdown"]
                    ):
                        self.miners[miner]["set"] = "on"

        # check if shutting down miners will help
        elif (
            max_tune_wattage / 2
        ) + min_shutdown_wattage + max_other_wattage < wattage:
            # tuneable inclusive since could be S9 BOS+ and S19 Stock, would rather shut down the S9, tuneable should always support shutdown
            useable_wattage = wattage - (
                min_tune_wattage + max_other_wattage + min_shutdown_wattage
            )
            for miner in sorted(
                [miner for miner in self.miners.values() if miner["shutdown"]],
                key=lambda x: x["max"],
                reverse=True,
            ):
                if miner["tune"]:
                    miner_min_watt_use = miner["max"] / 2
                    useable_wattage -= miner_min_watt_use - miner["min"]
                    if useable_wattage < 0:
                        useable_wattage += miner_min_watt_use - miner["min"]
                        self.miners[str(miner["miner"].ip)]["set"] = "off"
                else:
                    miner_min_watt_use = miner["max"]
                    useable_wattage -= miner_min_watt_use - miner["min"]
                    if useable_wattage < 0:
                        useable_wattage += miner_min_watt_use - miner["min"]
                        self.miners[str(miner["miner"].ip)]["set"] = "off"

            new_shutdown_wattage = sum(
                [
                    miner["max"] if miner["set"] == 0 else miner["min"]
                    for miner in self.miners.values()
                    if miner["shutdown"] and not miner["tune"]
                ]
            )
            new_tune_wattage = sum(
                [
                    miner["min"]
                    for miner in self.miners.values()
                    if miner["tune"] and miner["set"] == "off"
                ]
            )

            useable_wattage = wattage - (
                new_tune_wattage + max_other_wattage + new_shutdown_wattage
            )
            useable_miners = len(
                [m for m in self.miners.values() if (m["set"] == 0) and (m["tune"])]
            )

            if not useable_miners == 0:
                watts_per_miner = useable_wattage // useable_miners
                # loop through and set useable miners to wattage
                for miner in self.miners:
                    if (self.miners[miner]["set"] == 0) and (
                        self.miners[miner]["tune"]
                    ):
                        self.miners[miner]["set"] = watts_per_miner
                    elif self.miners[miner]["set"] == 0 and (
                        self.miners[miner]["shutdown"]
                    ):
                        self.miners[miner]["set"] = "on"

        # check if shutting down tuneable miners will do it
        elif min_tune_wattage + min_shutdown_wattage + max_other_wattage < wattage:
            # all miners that can be shutdown need to be
            for miner in self.miners:
                if (not self.miners[miner]["tune"]) and (
                    self.miners[miner]["shutdown"]
                ):
                    self.miners[miner]["set"] = "off"
            # calculate wattage usable by tuneable miners
            useable_wattage = wattage - (
                min_tune_wattage + max_other_wattage + min_shutdown_wattage
            )

            # loop through miners to see how much is actually useable
            # sort the largest first
            for miner in sorted(
                [
                    miner
                    for miner in self.miners.values()
                    if miner["tune"] and miner["shutdown"]
                ],
                key=lambda x: x["max"],
                reverse=True,
            ):
                # add min to useable wattage since it was removed earlier, and remove 1/2 tuner max
                useable_wattage -= (miner["max"] / 2) - miner["min"]
                if useable_wattage < 0:
                    useable_wattage += (miner["max"] / 2) - miner["min"]
                    self.miners[str(miner["miner"].ip)]["set"] = "off"

            new_tune_wattage = sum(
                [
                    miner["min"]
                    for miner in self.miners.values()
                    if miner["tune"] and miner["set"] == "off"
                ]
            )

            useable_wattage = wattage - (
                new_tune_wattage + max_other_wattage + min_shutdown_wattage
            )
            useable_miners = len(
                [m for m in self.miners.values() if (m["set"] == 0) and (m["tune"])]
            )

            if not useable_miners == 0:
                watts_per_miner = useable_wattage // useable_miners
                # loop through and set useable miners to wattage
                for miner in self.miners:
                    if (self.miners[miner]["set"] == 0) and (
                        self.miners[miner]["tune"]
                    ):
                        self.miners[miner]["set"] = watts_per_miner
                    elif self.miners[miner]["set"] == 0 and (
                        self.miners[miner]["shutdown"]
                    ):
                        self.miners[miner]["set"] = "on"
        else:
            raise APIError(
                f"Wattage setpoint is too low, setpoint: {wattage}W, min: {min_tune_wattage + min_shutdown_wattage + max_other_wattage}W"
            )  # PhaseBalancingError(f"Wattage setpoint is too low, setpoint: {wattage}W, min: {min_tune_wattage + min_shutdown_wattage + max_other_wattage}W")

        return self.miners
