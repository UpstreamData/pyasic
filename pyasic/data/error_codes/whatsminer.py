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

from dataclasses import dataclass, field, asdict


@dataclass
class WhatsminerError:
    """A Dataclass to handle error codes of Whatsminers."""

    error_code: int
    error_message: str = field(init=False)

    @property
    def error_message(self):  # noqa - Skip PyCharm inspection
        if self.error_code in ERROR_CODES:
            return ERROR_CODES[self.error_code]
        return "Unknown error type."

    @error_message.setter
    def error_message(self, val):
        pass

    def asdict(self):
        return asdict(self)


ERROR_CODES = {
    110: "Intake fan speed error.",
    111: "Exhaust fan speed error.",
    120: "Intake fan speed error.  Fan speed deviates by more than 2000.",
    121: "Exhaust fan speed error.  Fan speed deviates by more than 2000.",
    130: "Intake fan speed error.  Fan speed deviates by more than 3000.",
    131: "Exhaust fan speed error.  Fan speed deviates by more than 3000.",
    140: "Fan speed too high.",
    200: "Power probing error.  No power found.",
    201: "Power supply and configuration file don't match.",
    202: "Power output voltage error.",
    203: "Power protecting due to high environment temperature.",
    204: "Power current protecting due to high environment temperature.",
    205: "Power current error.",
    206: "Power input low voltage error.",
    207: "Power input current protecting due to bad power input.",
    210: "Power error.",
    213: "Power input voltage and current do not match power output.",
    216: "Power remained unchanged for a long time.",
    217: "Power set enable error.",
    218: "Power input voltage is lower than 230V for high power mode.",
    233: "Power output high temperature protection error.",
    234: "Power output high temperature protection error.",
    235: "Power output high temperature protection error.",
    236: "Power output high current protection error.",
    237: "Power output high current protection error.",
    238: "Power output high current protection error.",
    239: "Power output high voltage protection error.",
    240: "Power output low voltage protection error.",
    241: "Power output current imbalance error.",
    243: "Power input high temperature protection error.",
    244: "Power input high temperature protection error.",
    245: "Power input high temperature protection error.",
    246: "Power input high voltage protection error.",
    247: "Power input high voltage protection error.",
    248: "Power input high current protection error.",
    249: "Power input high current protection error.",
    250: "Power input low voltage protection error.",
    251: "Power input low voltage protection error.",
    253: "Power supply fan error.",
    254: "Power supply fan error.",
    255: "Power output high power protection error.",
    256: "Power output high power protection error.",
    257: "Input over current protection of power supply on primary side.",
    263: "Power communication warning.",
    264: "Power communication error.",
    267: "Power watchdog protection.",
    268: "Power output high current protection.",
    269: "Power input high current protection.",
    270: "Power input high voltage protection.",
    271: "Power input low voltage protection.",
    272: "Excessive power supply output warning.",
    273: "Power input too high warning.",
    274: "Power fan warning.",
    275: "Power high temperature warning.",
    300: "Right board temperature sensor detection error.",
    301: "Center board temperature sensor detection error.",
    302: "Left board temperature sensor detection error.",
    320: "Right board temperature reading error.",
    321: "Center board temperature reading error.",
    322: "Left board temperature reading error.",
    329: "Control board temperature sensor communication error.",
    350: "Right board temperature protecting.",
    351: "Center board temperature protecting.",
    352: "Left board temperature protecting.",
    360: "Hashboard high temperature error.",
    410: "Right board eeprom detection error.",
    411: "Center board eeprom detection error.",
    412: "Left board eeprom detection error.",
    420: "Right board eeprom parsing error.",
    421: "Center board eeprom parsing error.",
    422: "Left board eeprom parsing error.",
    430: "Right board chip bin type error.",
    431: "Center board chip bin type error.",
    432: "Left board chip bin type error.",
    440: "Right board eeprom chip number X error.",
    441: "Center board eeprom chip number X error.",
    442: "Left board eeprom chip number X error.",
    450: "Right board eeprom xfer error.",
    451: "Center board eeprom xfer error.",
    452: "Left board eeprom xfer error.",
    510: "Right board miner type error.",
    511: "Center board miner type error.",
    512: "Left board miner type error.",
    520: "Right board bin type error.",
    521: "Center board bin type error.",
    522: "Left board bin type error.",
    530: "Right board not found.",
    531: "Center board not found.",
    532: "Left board not found.",
    540: "Right board error reading chip id.",
    541: "Center board error reading chip id.",
    542: "Left board error reading chip id.",
    550: "Right board has bad chips.",
    551: "Center board has bad chips.",
    552: "Left board has bad chips.",
    560: "Right board loss of balance error.",
    561: "Center board loss of balance error.",
    562: "Left board loss of balance error.",
    600: "Environment temperature is too high.",
    610: "Environment temperature is too high for high performance mode.",
    701: "Control board no support chip.",
    710: "Control board rebooted as an exception.",
    712: "Control board rebooted as an exception.",
    800: "CGMiner checksum error.",
    801: "System monitor checksum error.",
    802: "Remote daemon checksum error.",
    2010: "All pools are disabled.",
    2020: "Pool 0 connection failed.",
    2021: "Pool 1 connection failed.",
    2022: "Pool 2 connection failed.",
    2030: "High rejection rate on pool.",
    2040: "The pool does not support asicboost mode.",
    2310: "Hashrate is too low.",
    2320: "Hashrate is too low.",
    2340: "Hashrate loss is too high.",
    2350: "Hashrate loss is too high.",
    5070: "Right hashboard water velocity is abnormal.",
    5071: "Center hashboard water velocity is abnormal.",
    5072: "Left hashboard water velocity is abnormal.",
    5110: "Right hashboard frequency up timeout.",
    5111: "Center hashboard frequency up timeout.",
    5112: "Left hashboard frequency up timeout.",
    8410: "Software version error.",
    100001: "/antiv/signature illegal.",
    100002: "/antiv/dig/init.d illegal.",
    100003: "/antiv/dig/pf_partial.dig illegal.",
}
