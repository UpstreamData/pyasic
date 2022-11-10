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

from dataclasses import asdict, dataclass, field, fields


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
        err_type = int(str(self.error_code)[:-2])
        err_subtype = int(str(self.error_code)[-2:-1])
        err_value = int(str(self.error_code)[-1:])
        try:
            select_err_subtype = ERROR_CODES[err_type][err_subtype]
            if err_value in select_err_subtype:
                return select_err_subtype[err_value]
            elif "n" in select_err_subtype:
                return select_err_subtype["n"].replace("{n}", str(err_value))  # noqa: picks up `select_err_subtype["n"]` as not being numeric?
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
        },
        1: {
            0: "Power error.",
            3: "Power input voltage and current do not match power output.",
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
    },
    4: {  # EEPROM error
        1: {"n": "Slot {n} eeprom detection error."},  # EEPROM detection error
        2: {"n": "Slot {n} eeprom parsing error."},  # EEPROM parsing error
        3: {"n": "Slot {n} chip bin type error."},  # chip bin error
        4: {"n": "Slot {n} eeprom chip number X error."},  # EEPROM chip number error
        5: {"n": "Slot {n} eeprom xfer error."},  # EEPROM xfer error
    },
    5: {  # hashboard error
        1: {"n": "Slot {n} miner type error."},  # board miner type error
        2: {"n": "Slot {n} bin type error."},  # chip bin type error
        3: {"n": "Slot {n} not found."},  # board not found error
        4: {"n": "Slot {n} error reading chip id."},  # reading chip id error
        5: {"n": "Slot {n} has bad chips."},  # board has bad chips error
        6: {"n": "Slot {n} loss of balance error."},  # loss of balance error
    },
    6: {  # env temp error
        0: {0: "Environment temperature is too high."},  # normal env temp error
        1: {  # high power env temp error
            0: "Environment temperature is too high for high performance mode."
        },
    },
    7: {  # control board error
        0: {1: "Control board no support chip."},
        1: {
            0: "Control board rebooted as an exception.",
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
    20: {  # pool error
        1: {0: "All pools are disabled."},  # all disabled error
        2: {"n": "Pool {n} connection failed."},  # pool connection failed error
        3: {0: "High rejection rate on pool."},  # rejection rate error
        4: {  # asicboost not supported error
            0: "The pool does not support asicboost mode."
        },
    },
    23: {  # hashrate error
        1: {0: "Hashrate is too low."},
        2: {0: "Hashrate is too low."},
        3: {0: "Hashrate loss is too high."},
        4: {0: "Hashrate loss is too high."},
    },
    50: {  # water velocity error
        7: {"n": "Slot {n} water velocity is abnormal."},  # abnormal water velocity
    },
    51: {  # frequency error
        7: {"n": "Slot {n} frequency up timeout."},  # frequency up timeout
    },
    84: {
        1: {0: "Software version error."},
    },
    1000: {
        0: {
            1: "/antiv/signature illegal.",
            2: "/antiv/dig/init.d illegal.",
            3: "/antiv/dig/pf_partial.dig illegal.",
        },
    },
}
