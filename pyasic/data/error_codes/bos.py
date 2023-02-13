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

from dataclasses import asdict, dataclass, fields


@dataclass
class BraiinsOSError:
    """A Dataclass to handle error codes of BraiinsOS+ miners.

    Attributes:
        error_message: The error message as a string.
        error_code: The error code as an int.  0 if the message is not assigned a code.
    """

    error_message: str
    error_code: int = 0

    @classmethod
    def fields(cls):
        return fields(cls)

    def asdict(self):
        return asdict(self)
