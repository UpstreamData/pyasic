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

from dataclasses import asdict, dataclass, field, fields

C_N_CODES = ["52", "53", "54", "55", "56"]


@dataclass
class WhatsminerError:
    """A Dataclass to handle error codes of Whatsminers.

    Attributes:
        error_code: The error code as an int.
        error_message: The error message as a string.  Automatically found from the error code.
    """

    error_code: int
    error_message: str = field(init=False)

    @classmethod
    def fields(cls):
        return fields(cls)

    @property
    def error_message(self):  # noqa - Skip PyCharm inspection
        if len(str(self.error_code)) > 3 and str(self.error_code)[:2] in C_N_CODES:
            # 55 error code base has chip numbers, so the format is
            # 55 -> board num len 1 -> chip num len 3
            err_type = 55
            err_subtype = int(str(self.error_code)[2:3])
            err_value = int(str(self.error_code)[3:])
        else:
            err_type = int(str(self.error_code)[:-2])
            err_subtype = int(str(self.error_code)[-2:-1])
            err_value = int(str(self.error_code)[-1:])
        try:
            select_err_type = ERROR_CODES[err_type]
            if err_subtype in select_err_type:
                select_err_subtype = select_err_type[err_subtype]
                if err_value in select_err_subtype:
                    return select_err_subtype[err_value]
                elif "n" in select_err_subtype:
                    return select_err_subtype[
                        "n"  # noqa: picks up `select_err_subtype["n"]` as not being numeric?
                    ].replace("{n}", str(err_value))
                else:
                    return "Unknown error type."
            elif "n" in select_err_type:
                select_err_subtype = select_err_type[
                    "n"  # noqa: picks up `select_err_subtype["n"]` as not being numeric?
                ]
                if err_value in select_err_subtype:
                    return select_err_subtype[err_value]
                elif "c" in select_err_subtype:
                    return (
                        select_err_subtype["c"]
                        .replace(  # noqa: picks up `select_err_subtype["n"]` as not being numeric?
                            "{n}", str(err_subtype)
                        )
                        .replace("{c}", str(err_value))
                    )
            else:
                return "Unknown error type."
        except KeyError:
            return "Unknown error type."

    @error_message.setter
    def error_message(self, val):
        pass

    def asdict(self):
        return asdict(self)


ERROR_CODES = {
    1: {  # Fan error
        0: {0: "Fan unknown."},
        1: {  # Fan speed error of 1000+
            0: "Intake fan speed error.",
            1: "Exhaust fan speed error.",
        },
        2: {  # Fan speed error of 2000+
            0: "Intake fan speed error.  Fan speed deviates by more than 2000.",
            1: "Exhaust fan speed error.  Fan speed deviates by more than 2000.",
        },
        3: {  # Fan speed error of 3000+
            0: "Intake fan speed error.  Fan speed deviates by more than 3000.",
            1: "Exhaust fan speed error.  Fan speed deviates by more than 3000.",
        },
        4: {0: "Fan speed too high."},  # High speed
    },
    2: {  # Power error
        0: {
            0: "Power probing error.  No power found.",
            1: "Power supply and configuration file don't match.",
            2: "Power output voltage error.",
            3: "Power protecting due to high environment temperature.",
            4: "Power current protecting due to high environment temperature.",
            5: "Power current error.",
            6: "Power input low voltage error.",
            7: "Power input current protecting due to bad power input.",
            8: "Power power error.",
            9: "Power voltage offset error.",
        },
        1: {
            0: "Power error.",
            1: "Power iout error, please reboot.",
            2: "Power vout error, reach vout border. Border: [1150, 1500]",
            3: "Power input voltage and current do not match power output.",
            4: "Power pin did not change.",
            5: "Power vout set error.",
            6: "Power remained unchanged for a long time.",
            7: "Power set enable error.",
            8: "Power input voltage is lower than 230V for high power mode.",
        },
        3: {
            3: "Power output high temperature protection error.",
            4: "Power output high temperature protection error.",
            5: "Power output high temperature protection error.",
            6: "Power output high current protection error.",
            7: "Power output high current protection error.",
            8: "Power output high current protection error.",
            9: "Power output high voltage protection error.",
        },
        4: {
            0: "Power output low voltage protection error.",
            1: "Power output current imbalance error.",
            3: "Power input high temperature protection error.",
            4: "Power input high temperature protection error.",
            5: "Power input high temperature protection error.",
            6: "Power input high voltage protection error.",
            7: "Power input high voltage protection error.",
            8: "Power input high current protection error.",
            9: "Power input high current protection error.",
        },
        5: {
            0: "Power input low voltage protection error.",
            1: "Power input low voltage protection error.",
            3: "Power supply fan error.",
            4: "Power supply fan error.",
            5: "Power output high power protection error.",
            6: "Power output high power protection error.",
            7: "Input over current protection of power supply on primary side.",
        },
        6: {
            3: "Power communication warning.",
            4: "Power communication error.",
            7: "Power watchdog protection.",
            8: "Power output high current protection.",
            9: "Power input high current protection.",
        },
        7: {
            0: "Power input high voltage protection.",
            1: "Power input low voltage protection.",
            2: "Excessive power supply output warning.",
            3: "Power input too high warning.",
            4: "Power fan warning.",
            5: "Power high temperature warning.",
        },
    },
    3: {  # temperature error
        0: {  # sensor detection error
            "n": "Slot {n} temperature sensor detection error."
        },
        2: {  # temperature reading error
            "n": "Slot {n} temperature reading error.",
            9: "Control board temperature sensor communication error.",
        },
        5: {"n": "Slot {n} temperature protecting."},  # temperature protection
        6: {0: "Hashboard high temperature error."},  # high temp
        8: {
            0: "Humidity sensor not found.",
            1: "Humidity sensor read error.",
            2: "Humidity sensor read error.",
            3: "Humidity sensor protecting.",
        },
    },
    4: {  # EEPROM error
        0: {0: "Eeprom unknown error."},
        1: {"n": "Slot {n} eeprom detection error."},  # EEPROM detection error
        2: {"n": "Slot {n} eeprom parsing error."},  # EEPROM parsing error
        3: {"n": "Slot {n} chip bin type error."},  # chip bin error
        4: {"n": "Slot {n} eeprom chip number X error."},  # EEPROM chip number error
        5: {"n": "Slot {n} eeprom xfer error."},  # EEPROM xfer error
    },
    5: {  # hashboard error
        0: {0: "Board unknown error."},
        1: {"n": "Slot {n} miner type error."},  # board miner type error
        2: {"n": "Slot {n} bin type error."},  # chip bin type error
        3: {"n": "Slot {n} not found."},  # board not found error
        4: {"n": "Slot {n} error reading chip id."},  # reading chip id error
        5: {"n": "Slot {n} has bad chips."},  # board has bad chips error
        6: {"n": "Slot {n} loss of balance error."},  # loss of balance error
        7: {"n": "Slot {n} xfer error chip."},  # xfer error
        8: {"n": "Slot {n} reset error."},  # reset error
        9: {"n": "Slot {n} frequency too low."},  # freq error
    },
    6: {  # env temp error
        0: {0: "Environment temperature is too high."},  # normal env temp error
        1: {  # high power env temp error
            0: "Environment temperature is too high for high performance mode."
        },
    },
    7: {  # control board error
        0: {0: "MAC address invalid", 1: "Control board no support chip."},
        1: {
            0: "Control board rebooted as an exception.",
            1: "Control board rebooted as exception and cpufreq reduced, please upgrade the firmware",
            2: "Control board rebooted as an exception.",
        },
    },
    8: {  # checksum error
        0: {
            0: "CGMiner checksum error.",
            1: "System monitor checksum error.",
            2: "Remote daemon checksum error.",
        }
    },
    9: {0: {1: "Power rate error."}},  # power rate error
    20: {  # pool error
        1: {0: "All pools are disabled."},  # all disabled error
        2: {"n": "Pool {n} connection failed."},  # pool connection failed error
        3: {0: "High rejection rate on pool."},  # rejection rate error
        4: {  # asicboost not supported error
            0: "The pool does not support asicboost mode."
        },
    },
    21: {1: {"n": "Slot {n} factory test step failed."}},
    23: {  # hashrate error
        1: {0: "Hashrate is too low."},
        2: {0: "Hashrate is too low."},
        3: {0: "Hashrate loss is too high."},
        4: {0: "Hashrate loss is too high."},
        5: {0: "Hashrate loss."},
    },
    50: {  # water velocity error/voltage error
        1: {"n": "Slot {n} chip voltage too low."},
        2: {"n": "Slot {n} chip voltage changed."},
        3: {"n": "Slot {n} chip temperature difference is too large."},
        4: {"n": "Slot {n} chip hottest temperature difference is too large."},
        7: {"n": "Slot {n} water velocity is abnormal."},  # abnormal water velocity
        8: {0: "Chip temp calibration failed, please restore factory settings."},
        9: {"n": "Slot {n} chip temp calibration check no balance."},
    },
    51: {  # frequency error
        1: {"n": "Slot {n} frequency up timeout."},  # frequency up timeout
        7: {"n": "Slot {n} frequency up timeout."},  # frequency up timeout
    },
    52: {"n": {"c": "Slot {n} chip {c} error nonce."}},
    53: {"n": {"c": "Slot {n} chip {c} too few nonce."}},
    54: {"n": {"c": "Slot {n} chip {c} temp protected."}},
    55: {"n": {"c": "Slot {n} chip {c} has been reset."}},
    56: {"n": {"c": "Slot {n} chip {c} does not return to the nonce."}},
    80: {
        0: {0: "The tool version is too low, please update."},
        1: {0: "Low freq."},
        2: {0: "Low hashrate."},
        3: {5: "High env temp."},
    },
    81: {
        0: {0: "Chip data error."},
    },
    82: {
        0: {0: "Power version error."},
        1: {0: "Miner type error."},
        2: {0: "Version info error."},
    },
    83: {
        0: {0: "Empty level error."},
    },
    84: {
        0: {0: "Old firmware."},
        1: {0: "Software version error."},
    },
    85: {
        "n": {
            0: "Hashrate substandard L{n}.",
            1: "Power consumption substandard L{n}.",
            2: "Fan speed substandard L{n}.",
            3: "Fan speed substandard L{n}.",
            4: "Voltage substandard L{n}.",
        },
    },
    86: {
        0: {0: "Missing product serial #."},
        1: {0: "Missing product type."},
        2: {
            0: "Missing miner serial #.",
            1: "Wrong miner serial # length.",
        },
        3: {
            0: "Missing power serial #.",
            1: "Wrong power serial #.",
            2: "Fault miner serial #.",
        },
        4: {
            0: "Missing power model.",
            1: "Wrong power model name.",
            2: "Wrong power model vout.",
            3: "Wrong power model rate.",
            4: "Wrong power model format.",
        },
        5: {0: "Wrong hash board struct."},
        6: {0: "Wrong miner cooling type."},
        7: {0: "Missing PCB serial #."},
    },
    87: {0: {0: "Miner power mismatch."}},
    99: {9: {9: "Miner unknown error."}},
    1000: {
        0: {
            0: "Security library error, please upgrade firmware",
            1: "/antiv/signature illegal.",
            2: "/antiv/dig/init.d illegal.",
            3: "/antiv/dig/pf_partial.dig illegal.",
        },
    },
    1001: {0: {0: "Security BTMiner removed, please upgrade firmware."}},
    1100: {
        0: {
            0: "Security illegal file, please upgrade firmware.",
            1: "Security virus 0001 is removed, please upgrade firmware.",
        }
    },
}
