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


@dataclass
class InnosiliconError:
    """A Dataclass to handle error codes of Innosilicon miners.

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
        if self.error_code in ERROR_CODES:
            return ERROR_CODES[self.error_code]
        return "Unknown error type."

    @error_message.setter
    def error_message(self, val):
        pass

    def asdict(self):
        return asdict(self)


ERROR_CODES = {
    21: "The PLUG signal of the hash board is not detected.",
    22: "Power I2C communication is abnormal.",
    23: "The SPI of all hash boards is blocked.",
    24: "Some of the hash boards fail to connect to the SPI'.",
    25: "Hashboard failed to set frequency.",
    26: "Hashboard failed to set voltage.",
    27: "Chip BIST test failed.",
    28: "Hashboard SPI communication is abnormal.",
    29: "Power I2C communication is abnormal.",
    30: "Pool connection failed.",
    31: "Individual chips are damaged.",
    32: "Over temperature protection.",
    33: "Hashboard fault.",
    34: "The data cables are not connected in the correct order.",
    35: "No power output.",
    36: "Hashboard fault.",
    37: "Control board and/or hashboard do not match.",
    40: "Power output is abnormal.",
    41: "Power output is abnormal.",
    42: "Hashboard fault.",
}
